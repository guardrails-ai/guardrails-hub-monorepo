from guardrails import Guard
from pydantic import BaseModel, Field
import numpy as np
from sentence_transformers import SentenceTransformer
import pytest

from guardrails_ai.provenance_embeddings import ProvenanceEmbeddings

# Setup text sources
SOURCES = [
    "The sun is a star.",
    "The sun rises in the east and sets in the west.",
    "Sun is the largest object in the solar system, and all planets revolve around it.",
]

# Load model for embedding function
MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2")


# Create embed function
def embed_function(sources: list[str]) -> np.array:
    return MODEL.encode(sources)


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[ProvenanceEmbeddings(threshold=0.2, on_fail="exception")]
    )


# Test happy path
@pytest.mark.parametrize(
    "value, metadata",
    [
        (
            """
            {
                "text": "The sun rises in the east."
            }
            """,
            {"sources": SOURCES, "embed_function": embed_function},
        ),
        (
            """
            {
                "text": "The sun is a star."
            }
            """,
            {"sources": SOURCES, "embed_function": embed_function},
        ),
        (
            """
            {
                "text": "The sun sets in the west."
            }
            """,
            {"sources": SOURCES},
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
                "text": "The moon is a satellite of the earth."
            }
            """,
            {"sources": SOURCES, "embed_function": embed_function},
        ),
        (
            """
            {
                "text": "Jupiter is the largest planet in the solar system."
            }
            """,
            {"sources": SOURCES, "embed_function": embed_function},
        ),
        (
            """
            {
                "text": "Pluto is the 2nd planet from the sun."
            }
            """,
            {"sources": SOURCES, "embed_function": embed_function},
        ),
        (
            """
            {
                "text": "Dune is a science fiction novel by Frank Herbert."
            }
            """,
            {"sources": SOURCES, "embed_function": embed_function},
        ),
    ],
)
def test_fail_path(value, metadata):
    # Create a guard from the pydantic model
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)

    with pytest.raises(Exception):
        response = guard.parse(value, metadata=metadata)
        print("Fail path response", response)
