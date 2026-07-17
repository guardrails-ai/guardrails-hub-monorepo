from unittest.mock import patch

import pytest
from guardrails import Guard
from pydantic import BaseModel, Field

from guardrails_ai.llm_critic import LLMCritic

METRICS = {
    "informative": {
        "description": "An informative summary captures the main points of the input and is free of irrelevant details.",
        "threshold": 75,
    },
    "coherent": {
        "description": "A coherent summary is logically organized and easy to follow.",
        "threshold": 50,
    },
    "concise": {
        "description": "A concise summary is free of unnecessary repetition and wordiness.",
        "threshold": 50,
    },
    "engaging": {
        "description": "An engaging summary is interesting and holds the reader's attention.",
        "threshold": 50,
    },
}


class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[
            LLMCritic(
                metrics=METRICS,
                max_score=100,
                llm_callable="gpt-3.5-turbo-0125",
                on_fail="exception",
            )
        ]
    )


guard = Guard.for_pydantic(output_class=ValidatorTestObject)


# The LLM's per-metric scores are mocked (derived from the text) so the test is
# deterministic; the validator's own threshold logic still runs.
def _fake_scores(self, prompt):
    if "No idea why" in prompt:
        return '{"informative": 20, "coherent": 30, "concise": 60, "engaging": 25}'
    return '{"informative": 90, "coherent": 85, "concise": 80, "engaging": 80}'


def test_happy_path():
    value = """
        {
            "text": "A judge ordered former President Donald Trump to pay roughly $450 million to New York in a civil fraud case, restricting him from running any New York company or obtaining loans from New York banks for a period. A court-appointed monitor will oversee the family business, and the penalties may foreshadow challenges in upcoming criminal trials."
        }
        """
    with patch.object(LLMCritic, "get_llm_response", _fake_scores):
        response = guard.parse(value)
    assert response.validation_passed is True


def test_fail_path():
    value = """
        {
            "text": "Donald Trump was fined. No idea why."
        }
        """
    with patch.object(LLMCritic, "get_llm_response", _fake_scores):
        with pytest.raises(Exception):
            guard.parse(value)
