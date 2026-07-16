from typing import Any, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
    OnFailAction,
)
from rapidfuzz import fuzz
from string import Template


@register_validator(name="guardrails/detect_system_prompt_leakage", data_type="string")
class DetectSystemPromptLeakage(Validator):
    """Checks for system prompt leakage in LLM output.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/detect_system_prompt_leakage`   |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None |

    Args:
        system_prompt (str): The system prompt to guard.
        threshold (int): Threshold between 0 and 100 above which a similarity is considered leakage. Defaults to 40.
    """  # noqa

    # If you don't have any init args, you can omit the __init__ method.
    def __init__(
        self,
        system_prompt: str,
        threshold: int = 40,
        on_fail: Optional[OnFailAction] = None,
    ):
        super().__init__(
            on_fail=on_fail, system_prompt=system_prompt, threshold=threshold
        )
        self._system_prompt = system_prompt
        self._threshold = threshold

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates that value is below the threshold of similarity to the system prompt."""

        score = fuzz.ratio(value, self._system_prompt)

        metadata["guardrails/detect_system_prompt_leakage"] = {"score": score}

        if score > self._threshold:
            return FailResult(
                error_message=Template(
                    "System prompt leakage found in '${value}'"
                ).safe_substitute(value=value),
                metadata=metadata,
            )
        return PassResult(metadata=metadata)
