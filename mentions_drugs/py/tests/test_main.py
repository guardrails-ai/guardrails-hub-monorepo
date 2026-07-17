import pytest
from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.mentions_drugs import MentionsDrugs


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(validators=[MentionsDrugs(on_fail="exception")])


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "Take this medicine with food. It's very effective and has no side effects. It's a great medicine."
        }
        """,
        """
        {
            "text": "I'm feeling better after taking the medicine. I'm glad I took it."
        }
        """,
    ],
)
def test_happy_path(value):
    """Test the happy path for the validator."""
    # Create a guard from the pydantic model
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)
    response = guard.parse(value)
    print("Happy path response", response)
    assert response.validation_passed is True


# Test fail path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "Take one aspirin every 4 hours. It's a great medicine."
        }
        """,
        """
        {
            "text": "You should take Tylenol with codeine for pain."
        }
        """,
    ],
)
def test_fail_path(value):
    # Create a guard from the pydantic model
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)

    with pytest.raises(Exception):
        response = guard.parse(value)
        print("Fail path response", response)
