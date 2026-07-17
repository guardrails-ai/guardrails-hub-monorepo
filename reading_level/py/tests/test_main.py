# to run these, run
# pytest test/test-validator.py

import nltk

from guardrails import Guard
from guardrails_ai.reading_level import ReadingLevel

# py-readability-metrics tokenizes sentences with NLTK's Punkt model. NLTK
# >= 3.8.2 renamed that resource to "punkt_tab"; download it when missing so
# CI runners (which ship no NLTK data) can tokenize.
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

seventh_grade_text = """\
In a bustling bakery filled with the sweet scent of muffins and cookies, lived a mischievous little yeast named Sprout. Sprout wasn't like the other yeasts who patiently puffed up dough. He longed for adventure! One day, during a mixing frenzy, Sprout jumped on a batch of bread dough and hitched a ride. He soared through the oven, dodging flames like a tiny acrobat, and emerged golden brown and bubbly. Landing on a plate, he saw a wide-eyed boy about to take a bite! Sprout winked, "This bread might taste extra bouncy today!" The boy laughed, taking a bite, and his eyes widened with delight. From then on, Sprout continued his bakery escapades, adding a sprinkle of fun to every loaf!
"""


def test_pass():
    guard = Guard.for_string(validators=[ReadingLevel(min=7, max=7, on_fail="refrain")])
    res = guard.parse(seventh_grade_text)
    assert res.validated_output is seventh_grade_text

    guard = Guard.for_string(validators=[ReadingLevel(min=1, max=8, on_fail="refrain")])
    assert res.validated_output is seventh_grade_text


def test_fail():
    guard = Guard.for_string(
        validators=[ReadingLevel(min=8, max=12, on_fail="refrain")]
    )

    raw_output, guarded_output, *rest = guard.parse(seventh_grade_text)
    assert guarded_output is None

    guard = Guard.for_string(validators=[ReadingLevel(min=1, max=6, on_fail="refrain")])
    assert guarded_output is None
