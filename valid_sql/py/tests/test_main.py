from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.valid_sql import ValidSQL
import pytest


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    code: str = Field(validators=[ValidSQL(on_fail="exception")])


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "code": "SELECT * FROM users"
        }
        """,
        """
        {
            "code": "SELECT id FROM users WHERE id = 1"
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
            "code": "SELEKT * FROMM users; DROP TABLE users"
        }
        """,
        """
        {
            "code": "SLCT id FOM users WHERE id = 1"
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
