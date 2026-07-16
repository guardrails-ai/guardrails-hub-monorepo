from typing import Any, Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)


@register_validator(name="guardrails/contains_string", data_type="string")
class ContainsString(Validator):
    """Validates that a string contains a substring.

    **Key Properties**

    | Property                      | Description         |
    | ----------------------------- | ------------------- |
    | Name for `format` attribute   | `contains_string`   |
    | Supported data types          | `string`            |
    | Programmatic fix              | None                |

    Args:
        substring (str): The substring to search for.
        on_fail (Optional[Callable]): A function to call when the validator fails. Defaults to None.
    """

    def __init__(
        self,
        substring: str,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail, substring=substring)
        self._substring = substring

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validates that a string contains a substring."""
        if self._substring not in value:
            return FailResult(
                error_message=f"{value} doesn't contain {self._substring}",
                fix_value="",
            )
        return PassResult()
