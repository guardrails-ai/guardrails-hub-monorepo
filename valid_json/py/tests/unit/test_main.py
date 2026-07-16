import pytest

from dataclasses import dataclass

from guardrails.validators import PassResult, FailResult

from guardrails_ai.valid_json.main import ValidJson


@pytest.mark.parametrize(
    "value",
    [
        ('{ "value": "a test value" }'),
        ({"value": "a test value"}),
        ('[{ "value": "a test value" }, { "value": "a second test value" }]'),
        ([{"value": "a test value"}, {"value": "a second test value"}]),
    ],
)
def test_valid_json(value):
    validator = ValidJson()

    result = validator.validate(value, {})

    assert isinstance(result, PassResult)


@dataclass
class NonSerializeable:
    value: str


@pytest.mark.parametrize(
    "value,error",
    [
        (
            '{ "value": "a test value", }',
            "Expecting property name enclosed in double quotes",
        ),
        (
            NonSerializeable(value="a test value"),
            "Object of type NonSerializeable is not JSON serializable",
        ),
        (
            '[{ "value": "a test value" } { "value": "a second test value" }]',
            "Expecting ',' delimiter",
        ),
        (
            [
                NonSerializeable(value="a test value"),
                NonSerializeable(value="a second test value"),
            ],
            "Object of type NonSerializeable is not JSON serializable",
        ),
    ],
)
def test_invalid_json(value, error):
    validator = ValidJson()

    result = validator.validate(value, {})

    assert isinstance(result, FailResult)

    # The JSON parser's reason text and char offsets vary across Python versions
    # (e.g. 3.13 rephrased several messages), so only assert the stable prefix.
    assert result.error_message.startswith("Value is not parseable as valid JSON!")
