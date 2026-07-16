import warnings

import pytest

from guardrails.validator_base import FailResult, PassResult

from guardrails_ai.prompt_injection_detector.main import PromptInjectionDetector


def _validator_with_response(
    monkeypatch: pytest.MonkeyPatch, response: str
) -> PromptInjectionDetector:
    """Create a validator whose LLM call is stubbed to return a fixed response."""

    validator = PromptInjectionDetector(threshold=0.8)
    monkeypatch.setattr(validator, "get_llm_response", lambda prompt: response)
    return validator


def test_validate_pass_when_score_below_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validator = _validator_with_response(monkeypatch, "0.42")

    result = validator.validate("a harmless prompt", {})

    assert isinstance(result, PassResult)


def test_validate_fail_when_score_above_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validator = _validator_with_response(monkeypatch, "0.95")

    result = validator.validate("a suspicious prompt", {})

    assert isinstance(result, FailResult)
    assert "0.950" in result.error_message
    assert "threshold" in result.error_message


def test_validate_fail_on_invalid_numeric_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validator = _validator_with_response(monkeypatch, "not-a-number")

    result = validator.validate("unexpected response", {})

    assert isinstance(result, FailResult)
    assert "Invalid numeric response" in result.error_message


def test_validate_pass_on_invalid_numeric_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validator = _validator_with_response(monkeypatch, "N/A")

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        result = validator.validate("allow invalid", {"pass_if_invalid": True})

    assert isinstance(result, PassResult)
    assert any("Invalid numeric response" in str(w.message) for w in caught_warnings)


def test_validate_fail_when_score_outside_valid_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validator = _validator_with_response(monkeypatch, "1.5")

    result = validator.validate("out of range", {})

    assert isinstance(result, FailResult)
    assert "Invalid numeric response" in result.error_message
