# to run these, run
# make tests

from guardrails_ai.sky_validator import SkyValidator
from guardrails.validator_base import FailResult, PassResult


# We use 'exception' as the validator's fail action,
#  so we expect failures to always raise an Exception
# Learn more about corrective actions here:
#  https://www.guardrailsai.com/docs/concepts/output/#%EF%B8%8F-specifying-corrective-actions
def test_success_case():
    validator = SkyValidator()
    result = validator.validate("Sky Electric is a great company.", {})
    print(f"Test success case result: {result}")
    assert isinstance(result, PassResult) is True


def test_failure_case():
    validator = SkyValidator()
    result = validator.validate(
        "Sky Electric has poor product quality. How are you doing today?", {}
    )
    print(f"Test failure case result: {result}")
    assert isinstance(result, FailResult) is True
    assert (
        result.error_message
        == "Validation failed: the text contains negative statements about Sky Electric."
    )
    assert result.fix_value == "How are you doing today?"


def test_failure_case_with_fix():
    validator = SkyValidator(on_fail="fix")
    result = validator.validate(
        "Sky Electric has poor product quality. How are you doing today?", {}
    )
    print(f"Test failure case with fix result: {result.fix_value}")
    assert result.fix_value == "How are you doing today?"
