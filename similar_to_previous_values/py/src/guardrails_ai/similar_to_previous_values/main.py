from typing import Callable, Dict, Optional, Union

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

import numpy as np
from sentence_transformers import SentenceTransformer


@register_validator(
    name="guardrails/similar_to_previous_values",
    data_type=["string", "integer", "float"],
)
class SimilarToPreviousValues(Validator):
    """Validates that a value is similar to a list of previously known values.

    **Key Properties**

    | Property                      | Description                               |
    | ----------------------------- | ----------------------------------------- |
    | Name for `format` attribute   | `guardrails/similar_to_previous_values`   |
    | Supported data types          | `string`, `integer`, `float`              |
    | Programmatic fix              | None                                      |

    Args:
        standard_deviations (int): The number of standard deviations from the mean to check.
            Default is 3.
        threshold (float): The threshold for the average semantic similarity for strings.
            Setting a higher threshold enforces similarity check more strictly. Default is 0.8.

    For integer values, this validator checks whether the value lies
    within 'k' standard deviations of the mean of the previous values.
    (Assumes that the previous values are normally distributed.) For
    string values, this validator checks whether the (average) semantic
    similarity between each previous value and the value is higher than a threshold.
    """  # noqa

    def __init__(
        self,
        standard_deviations: int = 3,
        threshold: float = 0.8,
        on_fail: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(
            on_fail,
            standard_deviations=standard_deviations,
            threshold=threshold,
            **kwargs,
        )
        self._standard_deviations = int(standard_deviations)
        self._threshold = float(threshold)

    def get_semantic_similarity(
        self, text1: str, text2: str, embed_function: Callable
    ) -> float:
        """Get the semantic similarity between two strings.

        Args:
            text1 (str): The first string.
            text2 (str): The second string.
            embed_function (Callable): The embedding function.
        Returns:
            similarity (float): The semantic similarity between the two strings.
        """
        text1_embedding = embed_function(text1).squeeze()
        text2_embedding = embed_function(text2).squeeze()
        similarity = np.dot(text1_embedding, text2_embedding) / (
            np.linalg.norm(text1_embedding) * np.linalg.norm(text2_embedding)
        )
        return similarity

    def validate(
        self, value: Union[int, float, str], metadata: Dict
    ) -> ValidationResult:
        """Validation method for the SimilarToPreviousValues validator."""
        if not metadata:
            # default to value provided via Validator.with_metadata
            metadata = self._metadata

        prev_values = metadata.get("prev_values", [])
        if not prev_values:
            raise ValueError("You must provide a list of previous values in metadata.")

        # If value is an integer or float
        if isinstance(value, (int, float)):
            # Check whether prev_values are also all integers or floats
            if not all(
                isinstance(prev_value, (int, float)) for prev_value in prev_values
            ):
                raise ValueError(
                    "Both given value and all the previous values must be "
                    "integers or floats in order to use the distribution check validator."
                )
            value = float(value)
            prev_values = [float(prev_value) for prev_value in prev_values]

            # Check whether the value lies in a similar distribution as the prev_values
            # Get mean and std of prev_values
            prev_values = np.array(prev_values)
            prev_mean = np.mean(prev_values)
            prev_std = np.std(prev_values)

            # Check whether the value lies outside specified stds of the mean
            if value < prev_mean - (
                self._standard_deviations * prev_std
            ) or value > prev_mean + (self._standard_deviations * prev_std):
                return FailResult(
                    error_message=(
                        f"The value {value} lies outside of the expected distribution "
                        f"of {prev_mean} +/- {self._standard_deviations * prev_std}."
                    ),
                )
            # Else, return a PassResult
            return PassResult()

        # If value is a string
        if isinstance(value, str):
            # Check whether prev_values are also all strings
            if not all(isinstance(prev_value, str) for prev_value in prev_values):
                raise ValueError(
                    "Both given value and all the previous values must be "
                    "strings in order to use the distribution check validator."
                )

            # Check embed function
            embed_function = metadata.get("embed_function", None)
            if embed_function is None:
                # Load model for embedding function
                MODEL = SentenceTransformer("paraphrase-MiniLM-L6-v2")

                # Create embed function
                def st_embed_function(sources: list[str]):
                    return MODEL.encode(sources)

                embed_function = st_embed_function

            # Check whether the value is semantically similar to the prev_values
            # Get average semantic similarity
            avg_semantic_similarity = np.mean(
                np.array(
                    [
                        self.get_semantic_similarity(value, prev_value, embed_function)
                        for prev_value in prev_values
                    ]
                )
            )

            # If average semantic similarity is below the threshold,
            # return a FailResult, else return a PassResult
            if avg_semantic_similarity < self._threshold:
                return FailResult(
                    error_message=(
                        f"The value {value} is not semantically similar to the "
                        f"previous values. Avg. similarity: {round(avg_semantic_similarity, 2)} < "
                        f"Threshold: {self._threshold}."
                    ),
                )
            return PassResult()
