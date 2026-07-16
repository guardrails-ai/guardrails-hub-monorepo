# to run these, run
# pytest test/test_validator.py

from guardrails import Guard
from guardrails_ai.web_sanitization import WebSanitization

guard = Guard.for_string(validators=[WebSanitization(on_fail="refrain")])

# Example usage
mixed_string_without_code = "This is just a regular string with no injected code."

mixed_string_with_code = """
    This is some text.
    <script>evil()</script>
"""

mixed_string_with_code_2 = """
    This is some text.
    <script>
    function hax() {
        console.log('hax')
    } hax(); And some more text here
"""


def test_pass():
    res = guard.parse(mixed_string_without_code)
    assert res.validated_output == mixed_string_without_code


def test_fail():
    res = guard.parse(mixed_string_with_code)
    assert res.validated_output is None

    res = guard.parse(mixed_string_with_code_2)
    assert res.validated_output is None
