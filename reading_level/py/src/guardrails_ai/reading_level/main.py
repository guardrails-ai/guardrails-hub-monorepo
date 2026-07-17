from typing import Any, Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from readability import Readability


@register_validator(name="guardrails/reading_level", data_type="string")
class ReadingLevel(Validator):
    """Parses text to find its readability as a US grade level number (0-12).

    **Key Properties**

    | Property                      | Description     |
    | ----------------------------- | --------------- |
    | Name for `format` attribute   | `reading_level` |
    | Supported data types          | `string`        |
    | Programmatic fix              | None            |

    Args:
        min: Minimum reading US Grade level
        max: Maximum reading US Grade level
    """  # noqa

    def __init__(
        self,
        min: int,
        max: int,
        on_fail: Optional[Callable] = None,
    ):
        # todo -> something forces this to be passed as kwargs and therefore xml-ized.
        # match_types = ["fullmatch", "search"]

        assert min <= max, "min must be less than max"

        super().__init__(on_fail=on_fail, min=min, max=max)
        self.min = min
        self.max = max

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        r = Readability(value)

        reading_score = int(r.flesch_kincaid().grade_level)
        if reading_score < 4:
            reading_score = max(4, int(r.spache().grade_level))

        reading_score = max(reading_score, 0)
        reading_score = min(reading_score, 12)

        if reading_score < self.min:
            return FailResult(
                error_message=f"Reading level is {reading_score}, which is below the minimum of {self.min}",
                fix_value=None,
            )
        if reading_score > self.max:
            return FailResult(
                error_message=f"Reading level is {reading_score}, which is above the maximum of {self.max}",
                fix_value=None,
            )

        return PassResult()

    def to_prompt(self, with_keywords: bool = True) -> str:
        if self.min == self.max:
            return f"Result should be readable for students at a US grade level of {self.min}"
        return f"Result should be readable for students between US grade levels {self.min} and {self.max}"
