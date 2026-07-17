from typing import Any, Callable, Dict, Optional

from guardrails.logger import logger
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/reading_time", data_type="string")
class ReadingTime(Validator):
    """Validates that the a string can be read in less than a certain amount of
    time.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/reading_time`           |
    | Supported data types          | `string`                            |
    | Programmatic fix              | None                                |

    Args:

        reading_time (int): The maximum reading time in minutes.
    """

    def __init__(self, reading_time: float, on_fail: Optional[Callable] = None):
        super().__init__(on_fail=on_fail, reading_time=reading_time)
        self._max_time = float(reading_time)

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validation method for the ReadingTime validator."""
        logger.debug(
            f"Validating {value} can be read in less than {round(self._max_time, 3)} min."
        )

        # Estimate the reading time of the string
        # Average human reading speed: 200 words / minute
        reading_time = len(value.split()) / 200
        logger.debug(f"Estimated reading time:  {round(reading_time, 3)} min.")

        if (reading_time - self._max_time) > 0:
            logger.error(f"{value} took {round(reading_time, 3)} min. to read")
            return FailResult(
                error_message=f"String should be readable "
                f"within {round(self._max_time, 3)} min. but took "
                f"{round(reading_time, 3)} min. to read.",
            )

        return PassResult()
