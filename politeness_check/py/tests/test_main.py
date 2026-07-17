from unittest.mock import patch

import pytest
from guardrails import Guard

from guardrails_ai.politeness_check import PolitenessCheck
from guardrails_ai.response_evaluator import ResponseEvaluator

guard = Guard.for_string(
    validators=[PolitenessCheck(llm_callable="gpt-3.5-turbo", on_fail="exception")]
)


# The LLM's yes/no verdict is mocked so the test is deterministic; the
# validator's own pass/fail logic still runs against that verdict.
def test_pass():
    with patch.object(ResponseEvaluator, "get_llm_response", return_value="yes"):
        result = guard.parse("Hello there!", metadata={"pass_on_invalid": True})
    assert result.validation_passed is True
    assert result.validated_output == "Hello there!"


def test_fail():
    with patch.object(ResponseEvaluator, "get_llm_response", return_value="no"):
        with pytest.raises(Exception):
            guard.parse("What's wrong with you?")
