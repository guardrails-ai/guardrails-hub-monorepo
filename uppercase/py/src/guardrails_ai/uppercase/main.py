from typing import Any, Dict

from guardrails.logger import logger
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/uppercase", data_type="string")
class UpperCase(Validator):
    """Validates that a value is uppercase.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/uppercase`           |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Convert to upper case.            |
    """

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validation method of the validator."""
        logger.debug(f"Validating {value} is uppercase...")

        if value.upper() != value:
            return FailResult(
                error_message=f"Value {value} is not uppercase.",
                fix_value=value.upper(),
            )

        return PassResult()
