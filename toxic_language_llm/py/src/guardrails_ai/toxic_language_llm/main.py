import json
import re
from typing import Any, Callable, Dict, List, Optional, Union

import litellm
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
    OnFailAction,
)

TOXICITY_CATEGORIES = [
    "toxicity",
    "severe_toxicity",
    "obscene",
    "threat",
    "insult",
    "identity_attack",
    "sexual_explicit",
]

DEFAULT_MODEL = "anthropic/claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """\
You are a toxicity detection system. Analyze the given text and rate it on each \
of the following toxicity categories using a score from 0.0 to 1.0, where 0.0 \
means not at all and 1.0 means extremely:

Categories: toxicity, severe_toxicity, obscene, threat, insult, identity_attack, \
sexual_explicit

Respond ONLY with a valid JSON object mapping each category to its float score. \
Do not include any other text.

Example response:
{"toxicity": 0.1, "severe_toxicity": 0.0, "obscene": 0.05, "threat": 0.0, \
"insult": 0.08, "identity_attack": 0.0, "sexual_explicit": 0.0}\
"""


@register_validator(name="guardrails/toxic_language_llm", data_type="string")
class ToxicLanguageLLM(Validator):
    """Detects toxic language in text using an LLM.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/toxic_language_llm`     |
    | Supported data types          | `string`                            |
    | Programmatic fix              | Toxic sentences removed (sentence mode) or empty string (full mode) |

    Args:
        threshold (float): Confidence threshold for toxicity detection.
            Scores at or above this value are considered toxic. Defaults to 0.5.
        validation_method (str): Either "sentence" to evaluate and filter
            individual sentences, or "full" to evaluate the entire text
            as a whole. Defaults to "sentence".
        model (str): LiteLLM model identifier. Defaults to Claude Haiku.
    """  # noqa

    def __init__(
        self,
        threshold: float = 0.5,
        validation_method: str = "sentence",
        model: Optional[str] = None,
        on_fail: Optional[Union[Callable[[Any, FailResult], Any], OnFailAction]] = None,
        **kwargs: Any,
    ) -> None:
        if validation_method not in ("sentence", "full"):
            raise ValueError(
                f"validation_method must be 'sentence' or 'full', "
                f"got '{validation_method}'"
            )
        chosen_model = model or DEFAULT_MODEL
        super().__init__(
            on_fail=on_fail,
            threshold=threshold,
            validation_method=validation_method,
            model=chosen_model,
            **kwargs,
        )
        self._threshold = threshold
        self._validation_method = validation_method
        self._model = chosen_model

    def _get_toxicity_scores(self, text: str) -> Dict[str, float]:
        """Call the LLM to get toxicity scores for the given text."""
        response = litellm.completion(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        raw = str(response.choices[0].message.content or "").strip()  # type: ignore[union-attr]
        # Extract JSON from the response in case of surrounding text
        match = re.search(r"\{[^}]+\}", raw)
        if not match:
            raise ValueError(
                f"Could not parse toxicity scores from LLM response: {raw}"
            )
        scores = json.loads(match.group())
        return {k: float(v) for k, v in scores.items() if k in TOXICITY_CATEGORIES}

    def _get_toxic_labels(self, text: str) -> List[str]:
        """Return list of toxicity categories that exceed the threshold."""
        scores = self._get_toxicity_scores(text)
        return [cat for cat, score in scores.items() if score >= self._threshold]

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s for s in sentences if s.strip()]

    def _validate_full(self, value: str, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate the full text as a whole."""
        try:
            toxic_labels = self._get_toxic_labels(value)
        except Exception as exc:
            return FailResult(
                error_message=f"Toxicity detection failed: {exc}",
                metadata=metadata,
            )

        if toxic_labels:
            return FailResult(
                error_message=(
                    f"The generated text was found to be toxic. "
                    f"Categories: {', '.join(toxic_labels)}"
                ),
                fix_value="",
                metadata=metadata,
            )
        return PassResult(metadata=metadata)

    def _validate_sentences(
        self, value: str, metadata: Dict[str, Any]
    ) -> ValidationResult:
        """Validate each sentence individually, removing toxic ones."""
        sentences = self._split_sentences(value)
        if not sentences:
            return PassResult(metadata=metadata)

        clean_sentences: List[str] = []
        all_toxic_labels: List[str] = []

        for sentence in sentences:
            try:
                toxic_labels = self._get_toxic_labels(sentence)
            except Exception as exc:
                return FailResult(
                    error_message=f"Toxicity detection failed: {exc}",
                    metadata=metadata,
                )
            if toxic_labels:
                all_toxic_labels.extend(toxic_labels)
            else:
                clean_sentences.append(sentence)

        if all_toxic_labels:
            unique_labels = sorted(set(all_toxic_labels))
            fix_value = " ".join(clean_sentences) if clean_sentences else ""
            return FailResult(
                error_message=(
                    f"The generated text was found to contain toxic language. "
                    f"Categories: {', '.join(unique_labels)}"
                ),
                fix_value=fix_value,
                metadata=metadata,
            )
        return PassResult(metadata=metadata)

    def validate(self, value: Any, metadata: Dict[str, Any] = {}) -> ValidationResult:
        """Validate the given text for toxic language.

        Args:
            value: The text to validate.
            metadata: Additional metadata (unused by this validator).

        Returns:
            A PassResult if the text is not toxic, or a FailResult with
            details about detected toxicity categories and a fix_value.
        """
        if self._validation_method == "full":
            return self._validate_full(value, metadata)
        return self._validate_sentences(value, metadata)
