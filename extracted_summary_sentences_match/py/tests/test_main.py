# to run these, run
# pytest test/test-validator.py

from guardrails import Guard
from guardrails_ai.extracted_summary_sentences_match import (
    ExtractedSummarySentencesMatch,
)

# We use 'refrain' as the validator's fail action,
#  so we expect failures to always result in a guarded output of None
# Learn more about corrective actions here:
#  https://www.guardrailsai.com/docs/concepts/output/#%EF%B8%8F-specifying-corrective-actions
guard = Guard.for_string(
    validators=[ExtractedSummarySentencesMatch(on_fail="refrain", threshold=0.775)]
)

metadata = {
    "filepaths": [
        "./tests/documents/helio-mechanics.txt",
        "./tests/documents/mass-and-influence.txt",
        "./tests/documents/star.txt",
    ]
}


def test_pass():
    test_output = "The sun is a star that rises in the east and sets in the west."
    response = guard.parse(test_output, metadata=metadata)
    assert response.validated_output is test_output


def test_fail():
    test_output = "b is a test value"
    response = guard.parse(test_output, metadata=metadata)
    assert response.validated_output is None
