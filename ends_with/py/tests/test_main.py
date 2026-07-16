from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.ends_with import EndsWith
import pytest


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(validators=[EndsWith(end="a", on_fail="exception")])


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "abcda"
        }
        """,
        """
        {
            "text": "xyzda"
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
            "text": "The quick brown fox jumps over the lazy dog. Fox fox fox fox fox."
        }
        """,
        """
        {
            "text": "Floopyland apple googglynock haha. It is settlement okay winter."
        }
        """,
        """
        {
            "text": "HSHAdhhghjgjhgfjhf jdhfjdhkfhkfd"
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
