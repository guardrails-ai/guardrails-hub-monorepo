from typing import Any, Dict, Union, Callable

from guardrails.logger import logger
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/ends_with", data_type=["string", "list"])
class EndsWith(Validator):
    """Validates that a list ends with a given value.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ---------------------------------   |
    | Name for `format` attribute   | `ends-with`                         |
    | Supported data types          | `string`, `list`                    |
    | Programmatic fix              | Append the given value if absent    |

    Args:
        end: The required last element.
    """

    def __init__(
        self, end: str, on_fail: Union[Callable[..., Any], None] = None, **kwargs
    ):
        super().__init__(on_fail=on_fail, end=end, **kwargs)
        self._end = end

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        logger.debug(f"Validating whether {value} ends with {self._end}...")

        if value[-1] != self._end:
            return FailResult(
                error_message=f"{value} must end with {self._end}",
                fix_value=(
                    value + [self._end]
                    if isinstance(value, list)
                    else value + self._end
                ),
            )

        return PassResult()
