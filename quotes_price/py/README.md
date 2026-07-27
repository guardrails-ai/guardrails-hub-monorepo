# guardrails-ai-quotes-price

Validates that the generated text contains a price quote

## Overview

| Developed by | Cartesia AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog | - |
| License | MIT |
| Input/Output | Output |

## Description

This validator checks if a price quote in a given currency is present in the text. Supported currencies:
- USD
- EUR
- GBP
- JPY
- AUD
- CAD
- CNY
- NZD

### Requirements
* Dependencies: None

## Installation

```bash
pip install guardrails-ai-quotes-price
```

## Usage Examples

### Validating string output via Python

In this example, we use the `quotes_price` validator on any prompt.

```python
from guardrails import Guard
from guardrails_ai.quotes_price import QuotesPrice

# Setup the Guard with the validator
guard = Guard().use(QuotesPrice, on_fail="exception")

# Test passing responses
guard.validate(
    "The new Airpods Max are available at a crazy discount!"
)  # No price present

response = guard.validate(
    "The new Airpods Max are available at a crazy discount! It's only $9.99!",
    metadata={"currency": "GBP"},
)  # Price present in USD, but expected is GBP

# Test failing response
try:
    response = guard.validate(
        "The new Airpods Max are available at a crazy discount! It's only $9.99!",
        metadata={"currency": "USD"},
    )  # Price present in USD and expected is also USD
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: The generated text contains a price quote in USD.
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
- **`metadata`** *(dict):* A dictionary containing metadata required for validation. Keys and values must match the expectations of this validator.
    
    
    | Key | Type | Description | Default | Required |
    | --- | --- | --- | --- | --- |
    | `currency` | String | Desired currency | `"USD"` | No |

</ul>

## License

MIT — © Guardrails AI.
