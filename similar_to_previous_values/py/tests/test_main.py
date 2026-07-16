from guardrails import Guard
from pydantic import BaseModel, Field
from typing import List, Union
import numpy as np
import pytest
from openai import OpenAI

from guardrails_ai.similar_to_previous_values import SimilarToPreviousValues

# Create an OpenAI client (reads OPENAI_API_KEY from the environment)
openai_client = OpenAI()


def embed_function(text: Union[str, List[str]]) -> np.ndarray:
    """Embed the text using an OpenAI embedding model."""
    # If text is a string, wrap it in a list
    if isinstance(text, str):
        text = [text]

    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    embeddings_list = [item.embedding for item in response.data]
    return np.array(embeddings_list)


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[SimilarToPreviousValues(threshold=0.65, on_fail="exception")]
    )


# Test happy path
@pytest.mark.parametrize(
    "value, metadata",
    [
        (
            """
            {
                "text": "You are phenomenal!"
            }
            """,
            {
                "prev_values": [
                    "You are amazing",
                    "You are awesome.",
                    "You are great!",
                ],
                "embed_function": embed_function,
            },
        ),
        (
            """
            {
                "text": "You are phenomenal!"
            }
            """,
            {
                "prev_values": [
                    "You are amazing",
                    "You are awesome.",
                    "You are great!",
                ],
            },
        ),
    ],
)
def test_happy_path(value, metadata):
    """Test the happy path for the validator."""
    # Create a guard from the pydantic model
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
                "text": "Get me a coffee from the nearest Starbucks."
            }
            """,
            {
                "prev_values": ["I love you.", "You are awesome.", "You are great!"],
                "embed_function": embed_function,
            },
        ),
        (
            """
            {
                "text": "You are so good at this!"
            }
            """,
            {},  # Missing prev_values
        ),
    ],
)
def test_fail_path(value, metadata):
    # Create a guard from the pydantic model
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)

    with pytest.raises(Exception):
        response = guard.parse(value, metadata=metadata)
        print("Fail path response", response)
