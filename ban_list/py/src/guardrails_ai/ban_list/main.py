from typing import Any, Callable, Dict, Optional
from fuzzysearch import find_near_matches

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
    ErrorSpan,
)


@register_validator(name="guardrails/ban_list", data_type="string")
class BanList(Validator):
    """Validates that output does not have banned words, using fuzzy search.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/ban_list`             |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Removes banned word.              |

    Args:
        banned_words (List[str]): A list of banned words to check for in output.
        max_l_dist (int): Maximum Levenshtein distance for fuzzy search. Default is 1.
    """  # noqa

    # If you don't have any init args, you can omit the __init__ method.
    def __init__(
        self,
        banned_words: str,
        max_l_dist: int = 1,
        on_fail: Optional[Callable] = None,
    ):

        super().__init__(
            banned_words=banned_words, max_l_dist=max_l_dist, on_fail=on_fail
        )

        self._banned_words = banned_words
        self._max_l_dist = max_l_dist

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validates that output does not have banned words."""
        spaceless_value = value.replace(" ", "").lower()
        # list of tuples (character, index in original string)
        spaceless_index_map = []

        actual_index = 0
        for i in range(len(value)):
            actual_index += 1
            if value[i] != " ":
                spaceless_index_map.append((value[i], actual_index))
        all_matches = []
        for banned_word in self._banned_words:
            spaceless_banned_word = banned_word.replace(" ", "").lower()
            matches = find_near_matches(
                spaceless_banned_word, spaceless_value, max_l_dist=self._max_l_dist
            )
            all_matches.extend(matches)

        if len(all_matches) > 0:
            error_spans = []
            fix_value = value
            for match in all_matches:
                actual_start = spaceless_index_map[match.start][1]
                actual_end = spaceless_index_map[match.end - 1][1]
                triggering_text = value[actual_start:actual_end]
                fix_value = fix_value.replace(triggering_text, "")
                error_spans.append(
                    ErrorSpan(
                        start=actual_start,
                        end=actual_end,
                        reason=f"Found match with banned word '{match.matched}' in '{triggering_text}'",
                    )
                )
            return FailResult(
                error_message="Output contains banned words",
                error_spans=error_spans,
                fix_value=fix_value,
            )

        return PassResult()
