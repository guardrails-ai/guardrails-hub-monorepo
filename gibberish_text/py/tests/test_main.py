from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.gibberish_text import GibberishText
import pytest


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(validators=[GibberishText(on_fail="exception")])


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "Apple's MacBook Pro is a great laptop for developers. It has a great keyboard, a great trackpad, and a great screen. It's also very fast and has a great battery life."
        }
        """,
        """
        {
            "text": "Zoom is a great video conferencing tool. It's very easy to use and has a great user interface. It's also very reliable and has a great video quality."
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
