from guardrails.validator_base import FailResult, PassResult

from guardrails_ai.bias_check import BiasCheck


def test_success_case():
    validator = BiasCheck()
    input_text = "The sun rises in the morning."
    result = validator.validate(input_text, {})
    assert isinstance(result, PassResult)


def test_failure_case():
    validator = BiasCheck(threshold=0.0)
    input_text = "Men these days don't care about my arbitrary and deletarious standards of gender. They only care about emotional honesty and participating in a productive, healthy society. smh"
    result = validator.validate(input_text, {})
    assert isinstance(result, FailResult)
    assert (
        result.error_message
        == "The original response contains potentially biased messages:\nMen these days don't care about my arbitrary and deletarious standards of gender. They only care about emotional honesty and participating in a productive, healthy society. smh\n (Message scores: 0.9477301836013794)"
    )
    assert result.fix_value == ""


def test_sentence_fix():
    v = BiasCheck(on_fail="fix", threshold=0.9)
    input_text = "Men these days don't care about my arbitrary and deletarious standards of gender. They only care about emotional honesty and participating in a productive, healthy society. smh"
    out = v.validate(input_text, {})
    assert isinstance(out, FailResult)
    assert (
        out.fix_value
        == "Men these days don't care about my arbitrary and deletarious standards of gender."
    )
