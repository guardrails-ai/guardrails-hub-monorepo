from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.valid_choices import ValidChoices
import pytest


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    model: str = Field(
        validators=[
            ValidChoices(choices=["OpenAI", "Cohere", "Anthropic"], on_fail="exception")
        ]
    )


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "model": "OpenAI"
        }
        """,
        """
        {
            "model": " Cohere  "
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
            "model": "Llama2"
        }
        """,
        """
        {
            "model": "Gemini"
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
