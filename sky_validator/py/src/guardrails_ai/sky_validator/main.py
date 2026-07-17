from typing import Any, Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/sky_validator", data_type="string")
class SkyValidator(Validator):
    """Validates that the input string does not contain negative statements about Sky Electric.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/sky_validator`        |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Removes negative statements about Sky Electric |

    Args:
        on_fail (Callable): The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
    """  # noqa

    def __init__(
        self,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail)

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates that the input string does not contain negative statements about Sky Electric."""
        negative_keywords = [
            "poor product quality",
            "bad company",
            "Sky Electric is bad",
            "Sky Electric infrastructure is poor",
            "negative reviews about Sky Electric",
        ]

        # Split the value into sentences
        sentences = value.split(". ")
        filtered_sentences = [
            sentence
            for sentence in sentences
            if not any(keyword in sentence for keyword in negative_keywords)
        ]
        filtered_value = ". ".join(filtered_sentences)

        if filtered_value != value:
            return FailResult(
                error_message="Validation failed: the text contains negative statements about Sky Electric.",
                fix_value=filtered_value,
            )
        return PassResult()
