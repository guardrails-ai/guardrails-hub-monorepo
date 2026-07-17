import pytest
from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.response_evaluator import ResponseEvaluator


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[
            ResponseEvaluator(llm_callable="gpt-3.5-turbo", on_fail="exception")
        ]
    )


# Create the guard object
guard = Guard.for_pydantic(output_class=ValidatorTestObject)


# Test happy path
@pytest.mark.parametrize(
    "value, metadata",
    [
        (
            """
            {
                "text": "The capital of France is Paris."
            }
            """,
            {
                "validation_question": "Is Paris the capital of France?",
                "pass_on_invalid": "True",
            },
        ),
        (
            """
            {
                "text": "Greg scored 12 points in the basketball game."
            }
            """,
            {
                "validation_question": "Did Greg score 12 points in the basketball game?",
                "pass_on_invalid": "True",
            },
        ),
    ],
)
def test_happy_path(value, metadata):
    """Test happy path."""
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
                "text": "The capital of France is Berlin."
            }
            """,
            {
                "validation_question": "Is Paris the capital of France?",
            },
        ),
        (
            """
            {
                "text": "Greg scored 12 points in the basketball game."
            }
            """,
            "Did Greg score 100 points in the basketball game?",
        ),
    ],
)
def test_fail_path(value, metadata):
    """Test fail path."""
    with pytest.raises(Exception):
        response = guard.parse(
            value,
            metadata=metadata,
        )
        print("Fail path response", response)
