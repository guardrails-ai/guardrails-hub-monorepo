import json
from typing import Any, Dict

from guardrails.validators import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(
    name="guardrails/valid_json", data_type=["string", "object", "list"]
)
class ValidJson(Validator):
    """Validates that a value is parseable as valid JSON.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/valid_json`           |
    | Supported data types          | `string`, `list`, `object`        |
    | Programmatic fix              | None                              |
    """  # noqa

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates that a value is parseable as valid JSON."""
        stringified = value
        parsed, error = (None, None)
        try:
            if not isinstance(value, str):
                stringified = json.dumps(value)

            parsed = json.loads(stringified)
        except json.decoder.JSONDecodeError as json_error:
            error = json_error
        except TypeError as type_error:
            error = type_error

        if error or not parsed:
            return FailResult(
                error_message=f"Value is not parseable as valid JSON! Reason: {str(error)}",
            )
        return PassResult()
