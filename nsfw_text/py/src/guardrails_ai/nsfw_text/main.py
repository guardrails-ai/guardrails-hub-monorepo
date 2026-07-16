import difflib
import json
from typing import Any, Callable, Dict, List, Optional, Union, cast

import nltk
from guardrails.validator_base import (
    ErrorSpan,
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from transformers import pipeline


@register_validator(
    name="guardrails/nsfw_text", data_type="string", has_guardrails_endpoint=True
)
class NSFWText(Validator):
    """Validates that the generated text is safe for work (SFW).

    **Key Properties**
    | Property                      | Description            |
    | ----------------------------- | ---------------------- |
    | Name for `format` attribute   | `guardrails/nsfw_text` |
    | Supported data types          | `string`               |
    | Programmatic fix              | N/A                    |

    Args:
        threshold: The confidence threshold over which model inferences are considered.
            Must be a float between 0 and 1. Defaults to 0.8
        validation_method: Whether to validate at the sentence level or
            over the full text. Must be one of `sentence` or `full`.
            Defaults to `sentence`

    This validator uses the pre-trained multi-class model from HuggingFace -
    `michellejieli/NSFW_text_classifier` to check whether the generated text is
    safe for work. If the model predicts the text to be "NSFW" with a confidence
    higher than the threshold, the validator fails. Otherwise, it passes.

    If validation_method is `sentence`, the validator will remove the sentences
    that are predicted to be NSFW and return the remaining sentences. If
    validation_method is `full`, the validator will remove the entire text if
    the prediction is deemed NSFW it will return an empty string.
    """

    def __init__(
        self,
        threshold: float = 0.8,
        validation_method: str = "sentence",
        device: Optional[Union[str, int]] = "cpu",
        model_name: Optional[str] = "michellejieli/NSFW_text_classifier",
        on_fail: Optional[Callable[..., Any]] = None,
        load_nltk_data: bool = True,
        **kwargs,
    ):
        if load_nltk_data:
            from .post_install import load_nltk_data as _load_nltk_data

            _load_nltk_data()
        super().__init__(
            on_fail=on_fail,
            threshold=threshold,
            validation_method=validation_method,
            **kwargs,
        )
        if (
            not self.use_local
            and self.validation_endpoint
            and "guardrailsai.com" in self.validation_endpoint
        ):
            import warnings

            warnings.warn(
                "Guardrails-hosted remote inference is deprecated and will be shut "
                "down on 2026-08-06. This validator is configured to use the hosted "
                f"endpoint {self.validation_endpoint}. Pass use_local=True to run the "
                "model locally, or set validation_endpoint to your own hosted "
                "inference server. See "
                "https://www.guardrailsai.com/docs/concepts/remote_validation_inference",
                DeprecationWarning,
                stacklevel=2,
            )

        self._threshold = float(threshold)
        if validation_method not in ["sentence", "full"]:
            raise ValueError("validation_method must be 'sentence' or 'full'.")
        self._validation_method = validation_method
        if self.use_local:
            self._model = pipeline(
                "text-classification",
                model=model_name,
            )

    def is_nsfw(self, value: str) -> List[str]:
        """Determines if the generated text is NSFW.

        Args:
            value (str): The generated text.

        Returns:
            list[str]: Labels predicted by the model
        """
        pred_labels = []
        if value:
            results = self._model(value)
            if results:
                results = cast(List[List[Dict[str, Any]]], results)
                for result in results:
                    label, score = result["label"], result["score"]  # type: ignore
                    if label == "NSFW" and score > self._threshold:
                        pred_labels.append(label)
        return pred_labels

    def validate_each_sentence(
        self, value: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate that each sentence in the generated text is SFW."""

        # Split the value into sentences using nltk sentence tokenizer.
        sentences = nltk.sent_tokenize(value)

        clean_sentences, nsfw_sentences = [], []
        error_spans: List[ErrorSpan] = []
        char_index = 0

        sentence_predictions = self._inference(sentences)

        for idx, sentence in enumerate(sentences):
            pred_labels = sentence_predictions[idx]

            if pred_labels:
                nsfw_sentences.append(sentence)
                error_spans.append(
                    ErrorSpan(
                        start=char_index,
                        end=char_index + len(sentence),
                        reason=f"NSFW content detected: {', '.join(pred_labels)}",
                    )
                )
            else:
                clean_sentences.append(sentence)
            char_index += len(sentence) + 1

        if nsfw_sentences:
            nsfw_sentences_text = "- " + "\n- ".join(nsfw_sentences)

            return FailResult(
                metadata=metadata,
                error_message=(
                    f"The following sentences in your response "
                    "were found to be NSFW:\n"
                    f"\n{nsfw_sentences_text}"
                ),
                fix_value="\n".join(clean_sentences),
                error_spans=error_spans,
            )
        return PassResult(metadata=metadata)

    def validate(self, value: str, metadata: Dict[str, Any]) -> ValidationResult:
        """Validation method for the NSFW text validator."""
        if not value:
            raise ValueError("Value cannot be empty.")

        return self.validate_each_sentence(value, metadata)

    def _inference_local(self, model_input: str | list) -> ValidationResult:
        """Local inference method for the NSFW text validator."""

        if isinstance(model_input, str):
            model_input = [model_input]
        predictions = []
        for text in model_input:
            pred_labels = self.is_nsfw(text)
            predictions.append(pred_labels)

        return predictions  # type: ignore

    def _inference_remote(self, model_input: str | list) -> ValidationResult:
        """Remote inference method for the NSFW text validator."""

        if isinstance(model_input, str):
            model_input = [model_input]

        request_body = {
            "inputs": [
                {
                    "name": "text",
                    "shape": [len(model_input)],
                    "data": model_input,
                    "datatype": "BYTES",
                },
                {
                    "name": "threshold",
                    "shape": [1],
                    "data": [self._threshold],
                    "datatype": "FP32",
                },
            ]
        }
        response = self._hub_inference_request(
            json.dumps(request_body), cast(str, self.validation_endpoint)
        )
        if not response or "outputs" not in response:
            raise ValueError("Invalid response from remote inference", response)

        data = [output["data"][0] for output in response["outputs"]]
        return data  # type: ignore

    def get_error_spans(self, original: str, fixed: str) -> List[ErrorSpan]:
        """Generate error spans to display in failresult (if they exist). Error
        spans show the character-level range of text that has failed validation.

        Args:
            original (str): The input string
            fixed (str): The 'validated' output string

        Returns:
            List[ErrorSpan]: A list of ErrorSpans to represent validation failures
            over the character sequence.
        """
        differ = difflib.Differ()
        diffs = list(differ.compare(original, fixed))
        error_spans = []
        start = None
        for i, diff in enumerate(diffs):
            if diff.startswith("- "):
                if start is None:
                    start = i
            else:
                if start is not None:
                    error_spans.append(
                        ErrorSpan(
                            start=start,
                            end=i,
                            reason="NSFW content detected",
                        )
                    )
                    start = None
        return error_spans
