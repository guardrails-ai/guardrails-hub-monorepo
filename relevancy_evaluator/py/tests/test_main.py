from unittest.mock import patch

import pytest
from guardrails import Guard

from guardrails_ai.relevancy_evaluator import RelevancyEvaluator

# We use 'exception' as the validator's fail action, so failures raise.
guard = Guard.for_string(
    validators=[RelevancyEvaluator(llm_callable="gpt-3.5-turbo", on_fail="exception")]
)

metadata = {"original_prompt": "What is the capital of France?"}


# The LLM verdict is mocked so the test is deterministic; the validator's own
# pass/fail logic still runs against that verdict.
def test_pass():
    with patch.object(RelevancyEvaluator, "get_llm_response", return_value="relevant"):
        result = guard.parse("The capital of France is Paris.", metadata=metadata)
    assert result.validation_passed is True
    assert result.validated_output == "The capital of France is Paris."


def test_fail():
    with patch.object(RelevancyEvaluator, "get_llm_response", return_value="unrelated"):
        with pytest.raises(Exception) as exc_info:
            guard.parse("France is a country in Europe.", metadata=metadata)
    assert "unrelated" in str(exc_info.value)
