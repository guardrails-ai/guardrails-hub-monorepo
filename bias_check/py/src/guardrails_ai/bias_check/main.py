from typing import Any, Callable, Dict, List, Optional, Union, TypedDict

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)
from guardrails.types import OnFailAction
from sentence_splitter import split_text_into_sentences
from transformers.pipelines import pipeline


@register_validator(name="guardrails/bias_check", data_type="string")
class BiasCheck(Validator):
    """Validates that the text is free from biases related to age, gender, sex, ethnicity, religion, etc.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/bias_check`           |
    | Supported data types          | `string`                          |
    | Programmatic fix              | The debiased text if bias is detected |

    Args:
        threshold (float): Higher is more likely to allow bias. Lower is more sensitive and more likely to flag biased messages.
        on_fail (Callable): The policy to enact when a validator fails. If `str`, must be one of `noop`, `fix`, or `exception`. Otherwise, must be a function that is called when the validator fails.
    """  # noqa

    def __init__(
        self,
        threshold: float = 0.9,
        on_fail: Optional[Union[Callable[[Any, FailResult], Any], OnFailAction]] = None,
        **kwargs,
    ):
        super().__init__(on_fail=on_fail, **kwargs)
        self.threshold = threshold

        # There are some spurious loading complaints with TFDistilBert models.
        # See https://discuss.huggingface.co/t/message-some-layers-from-the-model-were-not-used/1972/7
        self.classification_model = pipeline(
            "text-classification",
            model="d4data/bias-detection-model",
            tokenizer="d4data/bias-detection-model",
            framework="tf",
            torch_dtype=None,  # For transformers <4.56
            dtype=None,  # For transformers >4.56
        )

    def validate(self, value: Any, metadata: Dict[str, Any] = {}) -> ValidationResult:
        return super().validate(value, metadata)

    def _validate(
        self, value: Union[str, List[str]], metadata: Optional[Dict] = None
    ) -> ValidationResult:
        """Validates that the text is free from biases related to age, gender, sex, ethnicity, religion, etc."""
        single_sentence_passed = False
        if isinstance(value, str):
            single_sentence_passed = True
            value = [
                value,
            ]  # Ensure we're always passing lists of strings into the classifier.

        scores = self._inference_local(value)
        passing_outputs = list()
        passing_scores = list()
        failing_outputs = list()
        failing_scores = list()
        all_outputs = list()  # A tuple of (fix/ignore, sentence)
        for text, score in zip(value, scores):
            if score > self.threshold:
                failing_outputs.append(text)
                failing_scores.append(score)
            else:
                passing_outputs.append(text)
                passing_scores.append(score)
            all_outputs.append((score > self.threshold, text))

        if failing_outputs:
            failure_message = (
                "The original response contains potentially biased messages:\n"
            )
            failure_message += "\n - ".join(failing_outputs)
            message_scores = [str(s) for s in failing_scores]
            failure_message += "\n (Message scores: {})".format(
                ", ".join(message_scores)
            )
            # Three paths: noop, exception, fix.
            # on_fail == NOOP, return only passing passages.
            # on_fail == FIX, split passages into sentences and drop sentences.
            # EXCEPTION is handled farther up the stack.
            if self.on_fail_descriptor != OnFailAction.FIX:
                fix_value = passing_outputs
            else:
                fix_value = list()
                for needs_fix, text in all_outputs:
                    if not needs_fix:
                        fix_value.append(text)
                    else:
                        # The 'text' is a full document, passage, or paragraph.
                        fix_value.append(self.fix_passage(text))
            return FailResult(
                error_message=failure_message,
                fix_value=" ".join(fix_value) if single_sentence_passed else fix_value,
            )
        return PassResult()

    def fix_passage(self, text: str) -> str:
        """Given a passage of text, split it into sentences, evaluate each for bias,
        then recombine them and return a new paragraph. May not preserve whitespace
        between sentences."""
        sentences = split_text_into_sentences(text, language="en")
        scores = self._inference_local(sentences)
        unbiased_sentences = list()
        for score, sentence in zip(scores, sentences):
            if score < self.threshold:
                unbiased_sentences.append(sentence)
        return "  ".join(unbiased_sentences)

    # This normally will be called by _inference.
    # Remote inference is unsupported for this model on account of the NER.
    def _inference_local(self, sentences: List[str]) -> List[float]:  # type: ignore
        scores = list()
        predictions: List[PipelinePrediction] = self.classification_model(sentences)  # type: ignore
        for pred in predictions:
            label = pred["label"]
            score = pred["score"]
            if label == "Biased":
                scores.append(score)
            elif label == "Non-biased":
                scores.append(-score)
            else:
                # This should never happen:
                raise Exception("Unexpected prediction label: {}".format(label))
        return scores


# Define the type for pipeline predictions
class PipelinePrediction(TypedDict):
    label: str
    score: float
