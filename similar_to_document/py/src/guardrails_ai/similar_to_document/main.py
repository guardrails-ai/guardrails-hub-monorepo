from typing import Any, Callable, Dict, Optional

from guardrails.logger import logger
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from sentence_transformers import SentenceTransformer, util


@register_validator(name="guardrails/similar_to_document", data_type="string")
class SimilarToDocument(Validator):
    """Validates that a value is similar to the document.

    This validator checks if the value is similar to the document by checking
    the cosine similarity between the value and the document, using an
    embedding.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/similar_to_document`  |
    | Supported data types          | `string`                          |
    | Programmatic fix              | None                              |

    Args:
        document (str): The document string to use for similarity check.
        threshold (float): The minimum cosine similarity to be considered similar.  Defaults to 0.7.
        model (str): The embedding model to use.  Defaults to "all-MiniLM-L6-v2" from SentenceTransformers.
    """  # noqa

    def __init__(
        self,
        document: str,
        threshold: float = 0.7,
        model: str = "all-MiniLM-L6-v2",
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(
            on_fail=on_fail, document=document, threshold=threshold, model=model
        )

        self._document = document
        self._threshold = float(threshold)

        # Load the model
        try:
            print(f"Loading the model {model}. This may take a while...")
            self._model = SentenceTransformer(model)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load the model {model}. Please check the model name."
            ) from e

        # Compute the document embedding
        try:
            self._document_embedding = self._model.encode(document)
        except Exception as e:
            raise RuntimeError(
                f"Failed to encode the document {document} using the model {model}."
            ) from e

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Validation method for the SimilarToDocument validator."""

        logger.debug(f"Validating {value} is similar to the given document...")
        # Compute the value embedding
        try:
            value_embedding = self._model.encode(value)
        except Exception as e:
            raise RuntimeError(
                f"Failed to encode the value {value} using the model {self._model}."
            ) from e

        # Compute the cosine similarity between the document and the value
        try:
            similarity = util.cos_sim(
                self._document_embedding,
                value_embedding,
            )
        except Exception as e:
            raise RuntimeError(
                "Failed to compute the cosine similarity between the document and the value."
            ) from e

        # Convert the tensor to a float
        similarity = similarity[0][0].item()
        print(f"Similarity: {round(similarity, 3)}, Type: {type(similarity)}")

        # Compare the similarity with the threshold
        if similarity < self._threshold:
            return FailResult(
                error_message=f"Value {value} is not similar enough "
                f"to document {self._document}.",
            )

        return PassResult()
