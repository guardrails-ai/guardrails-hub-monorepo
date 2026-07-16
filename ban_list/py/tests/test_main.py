# to run these, run
# make tests

from guardrails import Guard
import pytest
from guardrails_ai.ban_list import BanList


@pytest.mark.parametrize(
    "validator, output, expected_result",
    [
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "hello world!",
            True,
        ),
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "bananers athens",
            False,
        ),
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=3,
                on_fail="noop",
            ),
            "boconut breeze",
            False,
        ),
        # test whitespaces
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "b   a   n   a   n   a",
            False,
        ),
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "c   o c onu       ttr  e e s",
            False,
        ),
        # test exact match
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "banana",
            False,
        ),
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "coconut trees",
            False,
        ),
        (
            BanList(
                banned_words=["banana", "athena", "coconut trees"],
                max_l_dist=1,
                on_fail="noop",
            ),
            "A T H E N A",
            False,
        ),
    ],
)
def test_combinations(validator, output, expected_result):
    guard = Guard.for_string(validators=[validator])
    result = guard.parse(output)
    assert result.validation_passed is expected_result
