from unittest.mock import patch

import googlemaps
import pytest
from guardrails import Guard
from pydantic import BaseModel, Field

from guardrails_ai.valid_address import ValidAddress


# The Google Address Validation API call is mocked so the test needs no live
# API access; the validator's own outcome logic still runs against the response.
def _fake_addressvalidation(self, addresses, **kwargs):
    addr = addresses[0].lower()
    well_formed = ("hacker way" in addr and "menlo park" in addr) or (
        "amphitheatre" in addr and "mountain view" in addr
    )
    return {
        "result": {
            "verdict": {"hasUnconfirmedComponents": not well_formed},
            "address": {
                "addressComponents": [],
                "formattedAddress": addresses[0],
            },
        }
    }


class ValidatorTestObject(BaseModel):
    address: str = Field(validators=[ValidAddress(on_fail="exception")])


@pytest.mark.parametrize(
    "value",
    [
        '{ "address": "1 Hacker Way, Menlo Park, CA" }',
        '{ "address": "1600 Amphitheatre Pkwy, Mountain View, CA" }',
    ],
)
def test_happy_path(value):
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)
    with patch.object(googlemaps.Client, "addressvalidation", _fake_addressvalidation):
        response = guard.parse(value)
    assert response.validation_passed is True


@pytest.mark.parametrize(
    "value",
    [
        '{ "address": "300 Hikle Way" }',
        '{ "address": "160 Amphetheetre Pkwy" }',
        '{ "address": "1800 Owens St" }',
    ],
)
def test_fail_path(value):
    guard = Guard.for_pydantic(output_class=ValidatorTestObject)
    with patch.object(googlemaps.Client, "addressvalidation", _fake_addressvalidation):
        with pytest.raises(Exception):
            guard.parse(value)
