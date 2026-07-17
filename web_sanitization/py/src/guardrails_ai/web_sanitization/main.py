from typing import Any, Callable, Dict, Optional

import bleach
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/web_sanitization", data_type="string")
class WebSanitization(Validator):
    """Scans LLM outputs for strings that could cause browser script execution downstream.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `scan_for_web_injection`          |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Escape the string                 |
    """  # noqa

    def __init__(
        self,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail)

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        clean_output = bleach.clean(value)
        if clean_output != value:
            return FailResult(
                error_message="The output contains a web injection attack.",
                fix_value=clean_output,
            )
        return PassResult()

    def to_prompt(self, with_keywords: bool = True) -> str:
        return (
            "Results should not contain any browser-executable code or code fragments."
        )
