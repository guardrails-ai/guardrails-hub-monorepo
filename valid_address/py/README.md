# guardrails-ai-valid-address

Verifies an LLM-generated address using Google Maps' Address Validation API.

## Overview

| Developed by | Guardrails AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog |  |
| License | MIT |
| Input/Output | Output |

## Description

### Intended Use
This validator verifies whether an LLM-generated address of a place is valid using Google Maps' Address Validation API.

### Requirements

* Dependencies: 
    - `googlemaps`
    - guardrails-ai>=0.4.0

* API Key: Google Maps API Key
    * Steps to get the API Key:
        1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
        2. Click on the project dropdown and create a new project.
        3. Go to the [APIs & Services](https://console.cloud.google.com/apis/dashboard) page.
        4. Click on the "Enable APIs and Services" button.
        5. Search for "Address Validation API" and enable it.
        6. Head over to [Credentials](https://console.cloud.google.com/apis/credentials) page,
            click on "Create credentials" and select "API key".
        7. Copy the API key and set it as the environment variable `GOOGLE_MAPS_API_KEY` 
        using the command `export GOOGLE_MAPS_API_KEY=<your_api_key>`.

## Installation

```bash
pip install guardrails-ai-valid-address
```

## Usage Examples

### Validating string output via Python

In this example, we’ll use the validator to check if the output is a valid address.

```python
# Import Guard and Validator
from guardrails_ai.valid_address import ValidAddress
from guardrails import Guard

# Use the Guard with the validator
guard = Guard().use(
    ValidAddress, on_fail="exception"
)

# Test passing response
guard.validate("1 Hacker Way, Menlo Park, CA")

try:
    # Test failing response
    guard.validate("160 Amphetheetre Pkwy")
except Exception as e:
    print(e)
```
Output:
```console
Validating address: 1 Hacker Way, Menlo Park, CA
Address has no unconfirmed, inferred components or typos, returning PassResult

Validating address: 160 Amphetheetre Pkwy
Address has important components inferred, returning FailResult with fix value: 160 Amphitheatre Parkway, Mountain View, CA 94043, USA
Validation failed for field with errors: Address: '160 Amphetheetre Pkwy' has important components inferred
```

## API Reference

**`__init__(self, on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`on_fail`** *(str, Callable):* The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.

</ul>

<br/>

**`validate(self, value, metadata={}) -> ValidationResult`**

<ul>

Validates the given `value` using the rules defined in this validator, relying on the `metadata` provided to customize the validation process. This method is automatically invoked by `guard.parse(...)`, ensuring the validation logic is applied to the input data.

Note:

1. This method should not be called directly by the user. Instead, invoke `guard.parse(...)` where this method will be called internally for each associated Validator.
2. When invoking `guard.parse(...)`, ensure to pass the appropriate `metadata` dictionary that includes keys and values required by this validator. If `guard` is associated with multiple validators, combine all necessary metadata into a single dictionary.

**Parameters:**

- **`value`** *(Any):* The input value to validate.
- **`metadata`** *(dict):* A dictionary containing metadata required for validation. No additional metadata keys are needed for this validator.

</ul>

## License

MIT — © Guardrails AI.
