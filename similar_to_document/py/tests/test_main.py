import pytest
from guardrails import Guard
from pydantic import BaseModel, Field
from guardrails_ai.similar_to_document import SimilarToDocument


# Create a pydantic model with a field that uses the custom validator
class ValidatorTestObject(BaseModel):
    text: str = Field(
        validators=[
            SimilarToDocument(
                document="""
                Large language models (LLM) are very large deep learning models that are pre-trained on vast amounts of data. 
                The underlying transformer is a set of neural networks that consist of an encoder and a decoder with self-attention capabilities. 
                The encoder and decoder extract meanings from a sequence of text and understand the relationships between words and phrases in it.
                Transformer LLMs are capable of unsupervised training, although a more precise explanation is that transformers perform self-learning. 
                It is through this process that transformers learn to understand basic grammar, languages, and knowledge.
                """,
                threshold=0.7,
                model="all-MiniLM-L6-v2",
                on_fail="exception",
            )
        ]
    )


# Create the guard object
guard = Guard.for_pydantic(output_class=ValidatorTestObject)


# Test happy path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "Large Language Models (LLMs) are a type of neural network that can be trained on large amounts of text data to generate human-like text. These models have been used in a variety of applications, including machine translation, text summarization, and question answering."
        }
        """,
    ],
)
def test_happy_path(value):
    """Test happy path."""
    response = guard.parse(value)
    print("Happy path response", response)
    assert response.validation_passed is True


# Test fail path
@pytest.mark.parametrize(
    "value",
    [
        """
        {
            "text": "Graph neural networks (GNNs) are specialized neural networks that can operate on graph data structures. These networks are designed to capture the relationships between nodes in a graph and can be used for a variety of tasks, including node classification, link prediction, and graph classification."
        }
        """,
    ],
)
def test_fail_path(value):
    """Test fail path."""
    with pytest.raises(Exception):
        response = guard.parse(
            value,
        )
        print("Fail path response", response)
