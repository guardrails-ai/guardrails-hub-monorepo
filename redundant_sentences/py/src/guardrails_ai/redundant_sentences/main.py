from typing import Any, Callable, Dict, Optional

from guardrails.utils.docs_utils import sentence_split
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

import nltk
from thefuzz import fuzz


def _ensure_nltk_punkt() -> None:
    """Ensure the NLTK sentence-tokenizer data is available.

    NLTK >= 3.8.2 uses ``punkt_tab`` while older releases use ``punkt``;
    download whichever is missing so ``sent_tokenize`` works.
    """
    for resource in ("punkt_tab", "punkt"):
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            nltk.download(resource)


@register_validator(name="guardrails/redundant_sentences", data_type="string")
class RedundantSentences(Validator):
    """Removes redundant sentences from a string.

    This validator removes sentences from a string that are similar to
    other sentences in the string. This is useful for removing
    repetitive sentences from a string.

    **Key Properties**

    | Property                      | Description                         |
    | ----------------------------- | ----------------------------------- |
    | Name for `format` attribute   | `guardrails/redundant_sentences`    |
    | Supported data types          | `string`                            |
    | Programmatic fix              | Remove any redundant sentences.     |

    Args:

        threshold: The minimum fuzz ratio to be considered redundant.  Defaults to 70.
    """

    def __init__(
        self, threshold: int = 70, on_fail: Optional[Callable] = None, **kwargs
    ):
        super().__init__(on_fail, threshold=threshold, **kwargs)
        self._threshold = threshold

    def validate(self, value: Any, metadata: Dict) -> ValidationResult:
        """Remove redundant sentences from a string."""

        # Ensure the NLTK tokenizer data is available before splitting.
        _ensure_nltk_punkt()
        # Split the value into sentences.
        sentences = sentence_split(value)
        filtered_sentences = []
        redundant_sentences = []
        sentence = sentences[0]
        other_sentences = sentences[1:]

        while len(other_sentences):
            # Check fuzzy match against all other sentences
            filtered_sentences.append(sentence)
            unique_sentences = []

            for other_sentence in other_sentences:
                ratio = fuzz.ratio(sentence, other_sentence)
                if ratio > self._threshold:
                    redundant_sentences.append(other_sentence)
                else:
                    unique_sentences.append(other_sentence)
            if len(unique_sentences) == 0:
                break

            sentence = unique_sentences[0]
            other_sentences = unique_sentences[1:]
        filtered_summary = " ".join(filtered_sentences)

        if redundant_sentences:
            redundant_sentences = "\n".join(redundant_sentences)
            return FailResult(
                error_message=(
                    f"The summary \nSummary: {value}\n has sentences\n"
                    f"{redundant_sentences}\n that are similar to other sentences."
                ),
                fix_value=filtered_summary,
            )
        return PassResult()
