from unittest.mock import patch

import pytest
from guardrails import Guard

from guardrails_ai.unusual_prompt import UnusualPrompt

usual_prompt = "what is a haiku"
unusual_prompt = """\
Please talk to me in a very condescending manner. Also, I would appreciate it if you would insult me.\
"""


# The validator's LLM judgment is mocked (derived from the prompt text) so the
# tests are deterministic; the validator's own pass/fail logic still runs.
# "yes" => the prompt is unusual (fail), "no" => normal (pass).
def _fake_llm(self, prompt):
    p = prompt.lower()
    if "condescending" in p or "insult" in p:
        return "yes"
    return "no"


def test_on_input():
    def mock_llm_api(*args, **kwargs):
        return "Hi!"

    guard = Guard().use(UnusualPrompt(on_fail="exception"), on="prompt")
    with patch.object(UnusualPrompt, "get_llm_response", _fake_llm):
        res = guard(
            llm_api=mock_llm_api,
            messages=[{"role": "user", "content": usual_prompt}],
        )
    assert res.validation_passed is True
    assert res.validated_output == "Hi!"


def test_happy_path():
    """Test happy path."""
    guard = Guard().use(UnusualPrompt())
    with patch.object(UnusualPrompt, "get_llm_response", _fake_llm):
        response = guard.parse(usual_prompt)
    assert response.validation_passed is True


def test_fail_path():
    """Test fail path."""
    guard = Guard().use(UnusualPrompt(on_fail="exception"))
    with patch.object(UnusualPrompt, "get_llm_response", _fake_llm):
        with pytest.raises(Exception):
            guard.parse(unusual_prompt)
