from typing import Any, Callable, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

import nltk
from transformers import pipeline


@register_validator(name="guardrails/gibberish_text", data_type="string")
class GibberishText(Validator):
    """Validates that the generated text is not gibberish.

    **Key Properties**
    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/gibberish_text`       |
    | Supported data types          | `string`                          |
    | Programmatic fix              | N/A                               |

    Args:
        threshold: The confidence threshold (model inference) for text "cleanliness".
            Defaults to 0.5.
        validation_method: Whether to validate at the sentence level or
            over the full text. Must be one of `sentence` or `full`.
            Defaults to `sentence`

    This validator uses the pre-trained multi-class model from HuggingFace -
    `madhurjindal/autonlp-Gibberish-Detector-492513457` to check whether
    the generated text is gibberish.
    If the model predicts the text to be "clean" with a confidence higher than
    the threshold, the validator passes. Otherwise, it fails.

    If validation_method is `sentence`, the validator will remove the sentences
    that are predicted to be gibberish and return the remaining sentences. If
    validation_method is `full`, the validator will remove the entire text if
    the prediction is deemed gibberish it will return an empty string.
    """

    def __init__(
        self,
        threshold: float = 0.5,
        validation_method: str = "sentence",
        on_fail: Optional[Callable] = None,
        load_nltk_data: bool = True,
        **kwargs,
    ):
        if load_nltk_data:
            from .post_install import load_nltk_data as _load_nltk_data

            _load_nltk_data()
        super().__init__(
            on_fail, threshold=threshold, validation_method=validation_method, **kwargs
        )
        self._threshold = float(threshold)

        if validation_method not in ["sentence", "full"]:
            raise ValueError("validation_method must be 'sentence' or 'full'.")
        self._validation_method = validation_method

        # Define the model, pipeline and labels
        self._model_name = "madhurjindal/autonlp-Gibberish-Detector-492513457"
        self._pipe = pipeline(
            "text-classification",
            model=self._model_name,
        )
        print("Pipeline setup successfully.")

    def is_gibberish(self, value: str) -> bool:
        """Determines if the generated text is gibberish.

        Args:
            value (str): The generated text.

        Returns:
            bool: Whether the generated text is gibberish or not.
        """
        result = self._pipe(value)
        if not result:
            raise RuntimeError("Failed to get model prediction.")

        pred_label, confidence = result[0]["label"], result[0]["score"]  # type: ignore
        if pred_label == "clean" and confidence > self._threshold:
            return False
        return True

    def validate_each_sentence(
        self, value: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that each sentence in the generated text is gibberish."""

        # Split the value into sentences using nltk sentence tokenizer.
        sentences = nltk.sent_tokenize(value)

        unsupported_sentences, supported_sentences = [], []
        for sentence in sentences:
            is_gibberish = self.is_gibberish(sentence)
            if is_gibberish:
                unsupported_sentences.append(sentence)
            else:
                supported_sentences.append(sentence)

        if unsupported_sentences:
            unsupported_sentences = "- " + "\n- ".join(unsupported_sentences)
            return FailResult(
                metadata=metadata,
                error_message=(
                    f"The following sentences in your response "
                    "were found to be gibberish:\n"
                    f"\n{unsupported_sentences}"
                ),
                fix_value="\n".join(supported_sentences),
            )
        return PassResult()

    def validate_full_text(
        self, value: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that the entire generated text is gibberish."""

        is_gibberish = self.is_gibberish(value)
        if is_gibberish:
            return FailResult(
                metadata=metadata,
                error_message="The generated text was found to be gibberish.",
            )
        return PassResult()

    def validate(self, value: str, metadata: Dict[str, Any]) -> ValidationResult:
        """Validation method of the GibberishText validator."""
        if self._validation_method == "sentence":
            return self.validate_each_sentence(value, metadata)

        if self._validation_method == "full":
            return self.validate_full_text(value, metadata)

        raise ValueError("validation_method must be 'sentence' or 'full'.")
