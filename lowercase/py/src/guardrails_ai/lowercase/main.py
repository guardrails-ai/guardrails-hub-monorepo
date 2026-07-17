from typing import Any, Dict

from guardrails.logger import logger
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/lowercase", data_type="string")
class LowerCase(Validator):
    """Validates that a value is lower case.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/lowercase`            |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Convert to lower case.            |
    """

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        logger.debug(f"Validating {value} is lowercase...")

        if value.lower() != value:
            return FailResult(
                error_message=f"Value {value} is not lowercase.",
                fix_value=value.lower(),
            )

        return PassResult()
