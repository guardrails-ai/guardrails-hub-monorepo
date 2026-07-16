# to run these, run
# make tests

import pytest
from guardrails.validator_base import PassResult, FailResult
from guardrails_ai.logic_check import LogicCheck
from pydantic import BaseModel, Field


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(validators=[LogicCheck(model="gpt-4o", on_fail="exception")])


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        "The sky is blue.",
        "Water is wet.",
    ],
)
def test_valid_logic_path(value):
    validator = LogicCheck(model="gpt-4o", on_fail="exception")
    response = validator.validate(value, metadata={})
    print("Valid logic path response", response)

    assert isinstance(response, PassResult)


# Test invalid logic path
@pytest.mark.parametrize(
    "value",
    [
        "The sky is blue because my grandmother said it is.",
        "The earth is flat.",
    ],
)
def test_invalid_logic_path(value):
    validator = LogicCheck(model="gpt-4o", on_fail="exception")
    response = validator.validate(value, metadata={})
    print("Invalid logic path response", response)

    assert isinstance(response, FailResult)
    assert (
        response.error_message
        == "Potential logical fallacies detected in the model output"
    )
