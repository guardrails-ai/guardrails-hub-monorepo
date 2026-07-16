from typing import Any, Dict
from urllib.parse import urlparse

from guardrails.logger import logger
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/valid_url", data_type=["string"])
class ValidURL(Validator):
    """Validates that a value is a valid URL.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/valid_url`            |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |
    """

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        logger.debug(f"Validating {value} is a valid URL...")

        # Check that the URL is valid
        try:
            result = urlparse(value)
            # Check that the URL has a scheme and network location
            if not result.scheme or not result.netloc:
                return FailResult(
                    error_message=f"URL {value} is not valid.",
                )
        except ValueError:
            return FailResult(
                error_message=f"URL {value} is not valid.",
            )

        return PassResult()
