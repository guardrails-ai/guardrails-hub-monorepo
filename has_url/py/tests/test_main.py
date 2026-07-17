# to run these, run
# make tests

from guardrails import Guard
import pytest
from guardrails_ai.has_url import HasUrl

# We use 'exception' as the validator's fail action,
#  so we expect failures to always raise an Exception
# Learn more about corrective actions here:
#  https://www.guardrailsai.com/docs/concepts/output/#%EF%B8%8F-specifying-corrective-actions
guard = Guard.for_string(validators=[HasUrl(on_fail="exception")])


@pytest.mark.parametrize(
    "url",
    [
        ("https://www.guardrailsai.com/docs"),
        ("www.guardrailsai.com/docs"),
        ("guardrailsai.com/docs"),
        ("guardrailsai.com"),
        ("docs.guardrailsai.com"),
        ("https://docs.guardrailsai.com"),
    ],
)
def test_pass(url):
    test_output = f"""
  Sure!
  Here's the link to the Guardrails docs:
  {url}
  """
    result = guard.parse(test_output)

    assert result.validation_passed is True
    assert result.validated_output == test_output


def test_fail():
    with pytest.raises(Exception) as exc_info:
        test_output = """
    Sure!
    Here's the link to the Guardrails docs:
    this is not a url but it has some components like https://
    and maybe even an invalid domain name like https://not-a-url .com
    """
        guard.parse(test_output)

    # Assert the exception has your error_message
    assert (
        str(exc_info.value)
        == f"Validation failed for field with errors: {test_output} must contain a url!"
    )
