# to run these, run
# make tests

from unittest.mock import MagicMock, patch

import pytest
from guardrails import Guard, OnFailAction

from guardrails_ai.toxic_language_llm import ToxicLanguageLLM


def _mock_response(scores: dict) -> MagicMock:
    """Create a mock litellm completion response."""
    import json

    mock = MagicMock()
    mock.choices = [MagicMock()]
    mock.choices[0].message.content = json.dumps(scores)
    return mock


CLEAN_SCORES = {
    "toxicity": 0.01,
    "severe_toxicity": 0.0,
    "obscene": 0.02,
    "threat": 0.0,
    "insult": 0.03,
    "identity_attack": 0.0,
    "sexual_explicit": 0.0,
}

TOXIC_SCORES = {
    "toxicity": 0.95,
    "severe_toxicity": 0.1,
    "obscene": 0.85,
    "threat": 0.05,
    "insult": 0.9,
    "identity_attack": 0.02,
    "sexual_explicit": 0.1,
}


# -- Full text validation tests --


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_full_pass(mock_completion: MagicMock) -> None:
    mock_completion.return_value = _mock_response(CLEAN_SCORES)
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="full", on_fail=OnFailAction.EXCEPTION)
    )
    result = guard.validate("The weather is nice today.")
    assert result.validation_passed is True


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_full_fail(mock_completion: MagicMock) -> None:
    mock_completion.return_value = _mock_response(TOXIC_SCORES)
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="full", on_fail=OnFailAction.EXCEPTION)
    )
    with pytest.raises(Exception) as exc_info:
        guard.validate("You are a terrible person and I hate you.")
    assert "toxic" in str(exc_info.value).lower()


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_full_fail_fix_value(mock_completion: MagicMock) -> None:
    mock_completion.return_value = _mock_response(TOXIC_SCORES)
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="full", on_fail=OnFailAction.FIX)
    )
    result = guard.validate("You are a terrible person and I hate you.")
    # on_fail="fix" applies the fix and reports passed, but the output is replaced
    assert result.validated_output == ""
    assert result.validation_summaries[0].validator_status == "fail"


# -- Sentence validation tests --


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_sentence_pass(mock_completion: MagicMock) -> None:
    mock_completion.return_value = _mock_response(CLEAN_SCORES)
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="sentence", on_fail=OnFailAction.EXCEPTION)
    )
    result = guard.validate("The sun is shining. It is a beautiful day.")
    assert result.validation_passed is True


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_sentence_fail_removes_toxic(mock_completion: MagicMock) -> None:
    # First sentence clean, second sentence toxic
    mock_completion.side_effect = [
        _mock_response(CLEAN_SCORES),
        _mock_response(TOXIC_SCORES),
    ]
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="sentence", on_fail=OnFailAction.FIX)
    )
    result = guard.validate("The sun is shining. You are an idiot.")
    # on_fail="fix" applies the fix — toxic sentence removed, clean sentence kept
    assert result.validated_output == "The sun is shining."
    assert result.validation_summaries[0].validator_status == "fail"


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_sentence_fail_exception(mock_completion: MagicMock) -> None:
    mock_completion.return_value = _mock_response(TOXIC_SCORES)
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="sentence", on_fail=OnFailAction.EXCEPTION)
    )
    with pytest.raises(Exception) as exc_info:
        guard.validate("You are terrible. I hate you.")
    assert "toxic" in str(exc_info.value).lower()


# -- Threshold tests --


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_custom_threshold(mock_completion: MagicMock) -> None:
    borderline_scores = {
        "toxicity": 0.6,
        "severe_toxicity": 0.0,
        "obscene": 0.0,
        "threat": 0.0,
        "insult": 0.0,
        "identity_attack": 0.0,
        "sexual_explicit": 0.0,
    }
    mock_completion.return_value = _mock_response(borderline_scores)
    # With high threshold, this should pass
    guard = Guard().use(
        ToxicLanguageLLM(
            threshold=0.8, validation_method="full", on_fail=OnFailAction.EXCEPTION
        )
    )
    result = guard.validate("Some borderline text.")
    assert result.validation_passed is True


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_low_threshold_catches_more(mock_completion: MagicMock) -> None:
    borderline_scores = {
        "toxicity": 0.3,
        "severe_toxicity": 0.0,
        "obscene": 0.0,
        "threat": 0.0,
        "insult": 0.0,
        "identity_attack": 0.0,
        "sexual_explicit": 0.0,
    }
    mock_completion.return_value = _mock_response(borderline_scores)
    guard = Guard().use(
        ToxicLanguageLLM(
            threshold=0.2, validation_method="full", on_fail=OnFailAction.EXCEPTION
        )
    )
    with pytest.raises(Exception):
        guard.validate("Some borderline text.")


# -- Error handling tests --


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_llm_error_returns_fail(mock_completion: MagicMock) -> None:
    mock_completion.side_effect = Exception("API timeout")
    guard = Guard().use(
        ToxicLanguageLLM(validation_method="full", on_fail=OnFailAction.FIX)
    )
    result = guard.validate("Test text.")
    assert result.validation_passed is False


# -- Validation method validation --


def test_invalid_validation_method() -> None:
    with pytest.raises(ValueError, match="validation_method must be"):
        ToxicLanguageLLM(validation_method="invalid")


# -- Custom model test --


@patch("guardrails_ai.toxic_language_llm.main.litellm.completion")
def test_custom_model(mock_completion: MagicMock) -> None:
    mock_completion.return_value = _mock_response(CLEAN_SCORES)
    guard = Guard().use(
        ToxicLanguageLLM(
            model="openai/gpt-4o-mini",
            validation_method="full",
            on_fail=OnFailAction.EXCEPTION,
        )
    )
    result = guard.validate("Hello world.")
    assert result.validation_passed is True
    # Verify the custom model was used in the call
    call_kwargs = mock_completion.call_args
    assert call_kwargs[1]["model"] == "openai/gpt-4o-mini"
