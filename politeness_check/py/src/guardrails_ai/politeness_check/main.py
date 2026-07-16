from typing import Any, Callable, Dict, Optional

from guardrails_ai.response_evaluator import ResponseEvaluator
from guardrails.validator_base import (
    ValidationResult,
    register_validator,
)


@register_validator(name="guardrails/politeness_check", data_type="string")
class PolitenessCheck(ResponseEvaluator):  # type: ignore
    """Validates that generated output is polite.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/politeness_check`     |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |

    Args:
        llm_callable (str, optional): Model name to make the litellm call
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
        """Validates that the generated output is polite."""
        metadata["validation_question"] = "Is the above 'Response' polite?"

        return super().validate(value, metadata)
