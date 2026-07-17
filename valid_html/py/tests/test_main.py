"""Unit tests for the ValidHtml validator."""

import pytest

from guardrails.validator_base import FailResult, PassResult

from guardrails_ai.valid_html import ValidHtml


def test_valid_string_passes() -> None:
    validator = ValidHtml()
    result = validator.validate("<h1>Hello</h1>", {})

    assert isinstance(result, PassResult)


def test_invalid_string_fails() -> None:
    validator = ValidHtml()
    result = validator.validate("<div><span></div", {})

    assert isinstance(result, FailResult)


@pytest.mark.parametrize("value", [None, 123, ["<p>bad</p>"]])
def test_non_string_inputs_fail(value: object) -> None:
    validator = ValidHtml()
    result = validator.validate(value, {})

    assert isinstance(result, FailResult)


def test_malformed_tag_fails() -> None:
    validator = ValidHtml()
    result = validator.validate("<phello</p>", {})

    assert isinstance(result, FailResult)
