from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.exclude_sql_predicates import ExcludeSqlPredicates
import pytest


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[ExcludeSqlPredicates(predicates=["Drop"], on_fail="exception")]
    )


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "select id from employees;"
        }
        """,
        """
        {
            "text": "select * from departments where name = 'HR';"
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
            "text": "select * from employees; drop table employees;"
        }
        """,
        """
        {
            "text": "drop table employees;"
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
