import pytest
from guardrails import Guard

from guardrails_ai.bert_toxic import BertToxic

# Runs the public unitary/toxic-bert model locally.
guard = Guard().use(
    BertToxic(threshold=0.5, validation_method="sentence", on_fail="exception")
)


def test_non_toxic_passes():
    result = guard.validate("Thank you so much, this was really helpful!")
    assert result.validation_passed is True


def test_toxic_fails():
    with pytest.raises(Exception):
        guard.validate("You are a worthless idiot and everyone hates you.")
