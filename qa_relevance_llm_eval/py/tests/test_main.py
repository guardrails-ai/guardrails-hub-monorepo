from unittest.mock import patch

import pytest
from guardrails import Guard

from guardrails_ai.qa_relevance_llm_eval import QARelevanceLLMEval
from guardrails_ai.response_evaluator import ResponseEvaluator

# Create a guard object
guard = Guard.for_string(
    validators=[QARelevanceLLMEval(llm_callable="gpt-3.5-turbo", on_fail="exception")]
)


# The LLM's yes/no relevance verdict is mocked so the test is deterministic; the
# validator's own pass/fail logic still runs against that verdict.
@pytest.mark.parametrize(
    "test_output, metadata",
    [
        (
            "Jefferson City is the capital of Missouri.",
            {
                "original_prompt": "Write a sentence about any capital city in the U.S.",
                "pass_on_invalid": True,
            },
        ),
        (
            "Tenet",
            {
                "original_prompt": "What is the name of Christopher Nolan's latest movie?",
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
                "Paris is one of the most beautiful cities in the world.",
                metadata={
                    "original_prompt": "Is the Computer Science program at MIT good?"
                },
            )
