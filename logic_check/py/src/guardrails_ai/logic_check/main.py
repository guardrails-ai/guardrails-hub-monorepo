from typing import Any, Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

import openai


@register_validator(name="guardrails/logic_check", data_type="string")
class LogicCheck(Validator):
    """Validates logical consistency and detects logical fallacies in the model output.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/logic_check`          |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Attempts to correct logical fallacies in the output |

    Args:
        model (string): The OpenAI model used for validation.
        on_fail (Callable): The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
    """  # noqa

    def __init__(
        self,
        model: str = "gpt-4o",
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail)
        self.model = model

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates logical consistency and detects logical fallacies in the model output."""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Detect any logical fallacies in the following text:\n\nOriginal: {value}\n\nReturn 'No fallacies found.' if the text is logically sound. If any logical fallacies are found, return only the corrected text.",
                    }
                ],
                max_tokens=1024,
                temperature=0.0,
            )
            corrected_text = (response.choices[0].message.content or "").strip()

            if corrected_text == "No fallacies found.":
                return PassResult()
            else:
                return FailResult(
                    error_message="Potential logical fallacies detected in the model output",
                    fix_value=f"Original: {value}\nCorrected: {corrected_text}",
                )
        except Exception as e:
            return FailResult(
                error_message=f"Error during validation: {str(e)}",
            )
