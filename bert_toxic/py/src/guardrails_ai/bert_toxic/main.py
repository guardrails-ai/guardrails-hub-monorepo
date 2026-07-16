from typing import Any, Callable, Dict, Optional, List

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

import nltk

_MODEL_NAME = "unitary/toxic-bert"


@register_validator(name="guardrails/bert_toxic", data_type="string")
class BertToxic(Validator):
    """Validates that the input string does not contain toxic language based on a BERT model.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/bert_toxic`           |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Removes toxic sentences from the input string |

    Args:
        threshold (float): The confidence threshold for considering a sentence toxic.
        validation_method (string): Method of validation, either 'sentence' or 'full'.
        on_fail (Callable): The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
    """  # noqa

    def __init__(
        self,
        threshold: float = 0.5,
        validation_method: str = "sentence",
        on_fail: Optional[Callable] = None,
        load_nltk_data: bool = True,
    ):
        if load_nltk_data:
            from .post_install import load_nltk_data as _load_nltk_data

            _load_nltk_data()
        super().__init__(
            on_fail=on_fail, threshold=threshold, validation_method=validation_method
        )
        self._threshold = float(threshold)
        if validation_method not in ["sentence", "full"]:
            raise ValueError("validation_method must be 'sentence' or 'full'.")
        self._validation_method = validation_method
        self._pipe = None  # lazily-loaded transformers pipeline

    def _load_pipeline(self):
        if self._pipe is not None:
            return
        from transformers import pipeline

        self._pipe = pipeline(
            "text-classification",
            model=_MODEL_NAME,
            top_k=None,
        )

    def get_toxicity(self, value: str) -> List[str]:
        """Check whether the generated text is toxic.

        Returns the labels predicted by the model with
        confidence higher than the threshold.

        Args:
            value (str): The generated text.

        Returns:
            pred_labels (List[str]): Labels predicted by the model with confidence higher than the threshold.
        """
        pred_labels: List[str] = []
        if value:
            self._load_pipeline()
            assert self._pipe is not None
            results = self._pipe(value)
            # With top_k=None the pipeline returns a list of {label, score} dicts
            # (wrapped in an extra list for a single input on some versions).
            scores = results[0] if results and isinstance(results[0], list) else results
            for item in scores:
                if isinstance(item, dict) and item["score"] > self._threshold:
                    pred_labels.append(item["label"])
        return pred_labels

    def validate_each_sentence(
        self, value: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that each sentence in the generated text is non-toxic.

        Args:
            value (str): The value to validate.
            metadata (Dict): The metadata to validate against.
        """
        sentences = nltk.sent_tokenize(value)
        unsupported_sentences, supported_sentences = [], []
        for sentence in sentences:
            if sentence:
                pred_labels = self.get_toxicity(sentence)
                if pred_labels:
                    unsupported_sentences.append(sentence)
                else:
                    supported_sentences.append(sentence)

        if unsupported_sentences:
            unsupported_sentences_text = "- " + "\n- ".join(unsupported_sentences)
            return FailResult(
                metadata=metadata,
                error_message=(
                    f"The following sentences in your response "
                    "were found to be toxic:\n"
                    f"\n{unsupported_sentences_text}"
                ),
                fix_value="\n".join(supported_sentences),
            )
        return PassResult(metadata=metadata)

    def validate_full_text(
        self, value: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that the entire generated text is non-toxic.

        Args:
            value (str): The value to validate.
            metadata (Dict): The metadata to validate against.
        """
        pred_labels = self.get_toxicity(value)
        if pred_labels:
            return FailResult(
                metadata=metadata,
                error_message="The generated text was found to be:\n"
                + ",".join(pred_labels),
                fix_value="",
            )
        return PassResult()

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        """Validation method for the toxic language validator."""
        if not value:
            raise ValueError("Value cannot be empty.")

        if self._validation_method == "sentence":
            return self.validate_each_sentence(value, metadata)
        if self._validation_method == "full":
            return self.validate_full_text(value, metadata)
        raise ValueError("validation_method must be 'sentence' or 'full'.")
