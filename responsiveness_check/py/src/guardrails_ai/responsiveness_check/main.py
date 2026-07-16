from typing import Any, Callable, Dict, Optional

from guardrails_ai.response_evaluator import ResponseEvaluator
from guardrails.validator_base import (
    ValidationResult,
    register_validator,
)


@register_validator(name="guardrails/responsiveness_check", data_type="string")
class ResponsivenessCheck(ResponseEvaluator):  # type: ignore
    """Validates that a generated output responds to the prompt given.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/responsiveness_check` |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |

    Args:
        prompt (string): The original prompt to the LLM.
        llm_callable (str, optional): Model name to make the litellm call.
            Defaults to `gpt-3.5-turbo`
        on_fail (Callable, optional): A function to call when validation fails.
            Defaults to None.
    """  # noqa

    def __init__(
        self,
        llm_callable: Optional[str] = "gpt-3.5-turbo",
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail, llm_callable=llm_callable)

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validates that the LLM response responds to the given prompt."""

        original_prompt = metadata.get("original_prompt", None)
        if original_prompt is None:
            raise RuntimeError(
                """Missing 'original_prompt' in metadata.
                Please provide the prompt, and try again.
                """
            )
        metadata[
            "validation_question"
        ] = f"""Does the above 'Response' answer the following 'Prompt'?
        Prompt:
        {original_prompt}
        """

        return super().validate(value, metadata)
