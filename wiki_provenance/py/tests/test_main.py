from unittest.mock import MagicMock, patch

import pytest
import wikipedia
from guardrails import Guard

from guardrails_ai.wiki_provenance import WikiProvenance

# Canned Wikipedia content so the test never hits the network.
_FAKE_CONTENT = (
    "Apple Inc. is an American multinational technology company headquartered "
    "in Cupertino, California, in Silicon Valley. Apple was founded by Steve "
    "Jobs, Steve Wozniak, and Ronald Wayne in April 1976 to develop and sell "
    "Wozniak's Apple I personal computer. As of March 2023, Apple is the "
    "world's largest technology company by revenue."
)


def _fake_page(*args, **kwargs):
    page = MagicMock()
    page.content = _FAKE_CONTENT
    return page


# Deterministic stand-in for the LLM's yes/no provenance verdict, derived from
# the sentence; the validator's own pass/fail logic still runs.
def _fake_eval(self, sentence):
    s = sentence.lower()
    if any(k in s for k in ("oil company", "mumbai", "ratan tata", "indian")):
        return "no"
    return "yes"


def _make_guard():
    with (
        patch.object(wikipedia, "search", return_value=["Apple Inc."]),
        patch.object(wikipedia, "page", _fake_page),
    ):
        validator = WikiProvenance(on_fail="exception", topic_name="Apple company")
    return Guard.for_string(validators=[validator])


@pytest.mark.parametrize(
    "value, metadata",
    [
        (
            "Apple Inc. is an American multinational technology company headquartered in Cupertino, California, in Silicon Valley.",
            {"pass_on_invalid": True},
        ),
        (
            "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976 to develop and sell Wozniak's Apple I personal computer.",
            {"pass_on_invalid": True},
        ),
    ],
)
def test_happy_path(value, metadata):
    guard = _make_guard()
    with patch.object(WikiProvenance, "get_evaluation", _fake_eval):
        response = guard.parse(value, metadata=metadata)
    assert response.validation_passed is True


@pytest.mark.parametrize(
    "value",
    [
        "Apple Inc. is an Indian oil company headquartered in Mumbai, India.",
        "As of March 2023, Apple is the world's largest technology company by revenue. It was founded in October 2001 by Ratan Tata.",
    ],
)
def test_fail_path(value):
    guard = _make_guard()
    with patch.object(WikiProvenance, "get_evaluation", _fake_eval):
        with pytest.raises(Exception):
            guard.parse(value)
