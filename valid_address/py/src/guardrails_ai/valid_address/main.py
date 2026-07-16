from typing import Any, Dict, Union, Callable
import os

from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

import googlemaps


@register_validator(name="guardrails/valid_address", data_type="string")
class ValidAddress(Validator):
    """
    **Key Properties**

    | Property                      | Description                               |
    | ----------------------------- | ----------------------------------------- |
    | Name for `format` attribute   | `guardrails/valid_address`                |
    | Supported data types          | `string`                                  |
    | Programmatic fix              | formattedAddress from API if applicable   |

    **Description**
    Validates an LLM-generated address using Google Maps' Address Validation API.

    Steps to get the Google Maps API key:
    1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2. Click on the project dropdown and create a new project.
    3. Go to the [APIs & Services](https://console.cloud.google.com/apis/dashboard) page.
    4. Click on the "Enable APIs and Services" button.
    5. Search for "Address Validation API" and enable it.
    6. Head over to [Credentials](https://console.cloud.google.com/apis/credentials) page,
         click on "Create credentials" and select "API key".
    7. Copy the API key and set it as the environment variable `GOOGLE_MAPS_API_KEY`.
    """

    def __init__(self, on_fail: Union[Callable[..., Any], None] = None, **kwargs):
        """Initialise the IsValidAddress validator"""

        super().__init__(on_fail, **kwargs)

        # Get the Google Maps API key from the environment variable
        gmaps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY", None)
        if gmaps_api_key is None:
            raise ValueError(
                "GOOGLE_MAPS_API_KEY environment variable not found. "
                "Please set the environment variable with your Google Maps API key."
            )

        # Initialize the Google Maps client
        self._gmaps_client = googlemaps.Client(key=gmaps_api_key)

        # List of component types to ignore when checking for inferred components
        self._ignored_component_types = ["postal_code", "postal_code_suffix", "country"]

    def get_outcome(self, value: str, api_response: Any) -> ValidationResult:
        """Get the validation outcome from the Google Maps Places API response.

        Process the response from the Google Maps Places API and return a ValidationResult.
        - If the address has any unconfirmed components, return a FailResult.
        - If the address has no unconfirmed components, but has important inferred components,
            return a FailResult with a fix value.
        - If the address has spelling corrected components, return a FailResult with a fix value.
        - If the address has NO unconfirmed, inferred components, or typos return a PassResult.

        Args:
            value (str): The address to validate
            api_response (Any): The response from the Google Maps Places API

        Returns:
            ValidationResult: The validation result
        """

        # Check if the address has unconfirmed or inferred components
        has_unconfirmed_components = api_response["result"]["verdict"].get(
            "hasUnconfirmedComponents", False
        )

        # Get the components of the address from the API response
        components = api_response["result"]["address"]["addressComponents"]

        # Check if any component NOT in the ignored list is inferred
        is_important_type_inferred = any(
            component["componentType"] not in self._ignored_component_types
            and component.get("inferred", False)
            for component in components
        )

        # Check if any component's spelling was corrected
        is_spell_corrected = any(
            component.get("spellCorrected", False) for component in components
        )

        # Check 1
        # If the address has any unconfirmed components,
        # return a FailResult with NO fix value
        if has_unconfirmed_components:
            print("Address has unconfirmed components, returning FailResult")
            return FailResult(
                error_message=f"Address: '{value}' has few unconfirmed and unverified components",
            )

        # Check 2
        # If the address has no unconfirmed components, but has
        # important components inferred, return a FailResult
        if is_important_type_inferred:
            print(
                "Address has important components inferred, returning FailResult with fix value:",
                api_response["result"]["address"]["formattedAddress"],
            )
            return FailResult(
                error_message=f"Address: '{value}' has important components inferred",
                fix_value=api_response["result"]["address"]["formattedAddress"],
            )

        # Check 3
        # If the address has spelling corrected components,
        # return a FailResult with the corrected address as the fix value
        if is_spell_corrected:
            print(
                "Address has spelling corrected components, returning FailResult with fix value:",
                api_response["result"]["address"]["formattedAddress"],
            )
            return FailResult(
                error_message=f"Address: '{value}' has some typos",
                fix_value=api_response["result"]["address"]["formattedAddress"],
            )

        # If the address has NO unconfirmed, inferred components or typos,
        print(
            "Address has no unconfirmed, inferred components or typos, returning PassResult"
        )
        return PassResult()

    def validate(self, value: str, metadata: Dict = {}) -> ValidationResult:
        """Validate the address using Google Maps' Address Validation API.

        Query the API, get the response and process it to get the validation outcome.

        Args:
            value (str): The address to validate
            metadata (Dict): The metadata for the address to validate

        Returns:
            ValidationResult: The validation result
        """

        # Strip the address of any leading/trailing whitespaces
        value = value.strip()
        print("Validating address:", value)

        # Get the validation response from the API
        try:
            validation_response = self._gmaps_client.addressvalidation(  # type: ignore
                [value],
                regionCode="US",
            )
        except Exception as e:
            raise RuntimeError(
                "API Error: Failed to get response from the Address Validation API."
            ) from e

        return self.get_outcome(value, validation_response)
