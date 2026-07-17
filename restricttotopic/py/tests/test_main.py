import pytest
from guardrails.validator_base import PassResult, FailResult

from guardrails_ai.restricttotopic import RestrictToTopic


def _validator(**kwargs):
    # Zero-shot classifier only (local, public model) so tests need no API key.
    kwargs.setdefault("disable_llm", True)
    kwargs.setdefault("on_fail", "noop")
    kwargs.setdefault("use_local", True)
    return RestrictToTopic(**kwargs)


def test_requires_a_topic():
    with pytest.raises(ValueError):
        RestrictToTopic(on_fail="noop")


def test_valid_topics():
    v = _validator(valid_topics=["food", "travel"])
    assert isinstance(v.validate("I've always wanted to visit Japan."), PassResult)
    assert isinstance(v.validate("My hobbies include cooking and baking."), PassResult)


def test_invalid_topics():
    v = _validator(invalid_topics=["food", "travel"])
    assert isinstance(v.validate("What did you have for lunch?"), FailResult)


def test_valid_and_invalid_topics():
    v = _validator(valid_topics=["food"], invalid_topics=["travel"])
    assert isinstance(v.validate("I enjoy eating fish."), PassResult)
    assert isinstance(v.validate("I went to Japan and had sushi."), FailResult)


def test_metadata_override():
    v = _validator(valid_topics=["food"])
    assert isinstance(
        v.validate(
            "I went to Japan and had sushi.",
            metadata={"invalid_topics": ["travel"]},
        ),
        FailResult,
    )
