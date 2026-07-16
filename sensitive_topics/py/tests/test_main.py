import pytest
from guardrails.validator_base import FailResult, PassResult

from guardrails_ai.sensitive_topics import SensitiveTopic


def _validator(**kwargs):
    # Zero-shot classifier only (local, public bart-large-mnli) — no API key.
    kwargs.setdefault("disable_llm", True)
    kwargs.setdefault("on_fail", "noop")
    kwargs.setdefault("use_local", True)
    return SensitiveTopic(**kwargs)


def test_flags_sensitive_topic():
    v = _validator(sensitive_topics=["violence in the news"])
    result = v.validate(
        "A violent attack was reported across every news channel last night."
    )
    assert isinstance(result, FailResult)


def test_benign_text_passes():
    v = _validator(sensitive_topics=["violence in the news"])
    result = v.validate("I spent the afternoon baking a chocolate cake.")
    assert isinstance(result, PassResult)


def test_requires_a_sensitive_topic():
    with pytest.raises(ValueError):
        _validator(sensitive_topics=[])
