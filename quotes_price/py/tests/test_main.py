import pytest
from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.quotes_price import QuotesPrice


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(validators=[QuotesPrice(on_fail="exception")])


# Test happy path
@pytest.mark.parametrize(
    "value, metadata",
    [
        (
            """
            {
                "text": "The price of a loaf of bread is not yet known."
            }
            """,
            {},
        ),
        (
            """
            {
                "text": "The price is $131.45."
            }
            """,
            {
                "currency": "JPY",
            },
        ),
    ],
)
def test_happy_path(value, metadata):
    """Test happy path."""
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)
    response = guard.parse(value, metadata=metadata)
    print("Happy path response", response)
    assert response.validation_passed is True


# Test fail path
@pytest.mark.parametrize(
    "value, metadata",
    [
        (
            """
            {
                "text": "The price of a loaf of bread is $1.50."
            }
            """,
            {
                "currency": "USD",
            },
        ),
        (
            """
            {
                "text": "The Windsor castle tour costs £20.00."
            }
            """,
            {
                "currency": "GBP",
            },
        ),
    ],
)
def test_fail_path(value, metadata):
    """Test fail path."""
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)
    with pytest.raises(Exception):
        response = guard.parse(
            value,
            metadata=metadata,
        )
        print("Fail path response", response)
