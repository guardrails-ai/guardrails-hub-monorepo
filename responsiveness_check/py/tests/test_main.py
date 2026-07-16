from unittest.mock import patch

import pytest
from guardrails import Guard

from guardrails_ai.responsiveness_check import ResponsivenessCheck
from guardrails_ai.response_evaluator import ResponseEvaluator

guard = Guard.for_string(validators=[ResponsivenessCheck(on_fail="exception")])


# The LLM's yes/no verdict is mocked so the test is deterministic; the
# validator's own pass/fail logic still runs against that verdict.
@pytest.mark.parametrize(
    "test_output, metadata",
    [
        (
            "Jefferson City is the capital of Missouri.",
            {
                "original_prompt": "What is the capital of Missouri?",
                "pass_on_invalid": True,
            },
        ),
        (
            "Kansas City is the capital of Missouri.",
            {
                "original_prompt": "What is the capital of Missouri?",
                "pass_on_invalid": True,
            },
        ),
    ],
)
def test_pass(test_output, metadata):
    with patch.object(ResponseEvaluator, "get_llm_response", return_value="yes"):
        result = guard.parse(test_output, metadata=metadata)
    assert result.validation_passed is True
    assert result.validated_output == test_output


def test_fail_non_responsive():
    with patch.object(ResponseEvaluator, "get_llm_response", return_value="no"):
        with pytest.raises(Exception):
            guard.parse(
                "Paris is the capital of France.",
                metadata={"original_prompt": "What is the capital of Missouri?"},
            )
