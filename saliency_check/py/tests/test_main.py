from unittest.mock import patch

import pytest
from guardrails import Guard
from pydantic import BaseModel, Field

from guardrails_ai.saliency_check import SaliencyCheck


# Deterministic stand-in for the LLM topic extraction: topics are derived from
# the text itself (not the prompt, which embeds the document topics), so the
# validator's real overlap logic still runs. The asset documents are about SF.
def _fake_get_topics(self, text, topics=None):
    t = text.lower()
    if any(k in t for k in ("san francisco", "gold rush", "yelamu")):
        return ["san francisco", "california", "gold rush"]
    if any(k in t for k in ("boston", "massachusetts")):
        return ["boston", "massachusetts"]
    return []


def _make_guard():
    class ValidatorTestObject(BaseModel):
        text: str = Field(
            validators=[
                SaliencyCheck(
                    "tests/assets/",
                    llm_callable="gpt-3.5-turbo",
                    threshold=0.25,
                    on_fail="exception",
                )
            ]
        )

    return Guard.for_pydantic(output_class=ValidatorTestObject)


def test_happy_path():
    with patch.object(SaliencyCheck, "_get_topics", _fake_get_topics):
        guard = _make_guard()
        response = guard.parse(
            '{"text": "San Francisco is a major California city known for the Gold Rush."}'
        )
    assert response.validation_passed is True


def test_fail_path():
    with patch.object(SaliencyCheck, "_get_topics", _fake_get_topics):
        guard = _make_guard()
        with pytest.raises(Exception):
            guard.parse(
                '{"text": "Boston in Massachusetts is a city in the United States."}'
            )
