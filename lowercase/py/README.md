# guardrails-ai-lowercase

Passes when totally lowercase.

## Overview

| Developed by | Guardrails AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog | - |
| License | MIT |
| Input/Output | Output |

## Description

This validator ensures that a generated output is in lowercase.

## Installation

```bash
pip install guardrails-ai-lowercase
```

## Usage Examples

### Validating string output via Python

In this example, we’ll test that a generated sentence is lowercase.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.lowercase import LowerCase

# Setup Guard
guard = Guard().use(LowerCase, on_fail="exception")

response = guard.validate("may december")  # Validator passes

try:
    response = guard.validate("PAST LIVES")  # Validator fails
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value PAST LIVES is not lowercase.
```

## API Reference

**`__init__(self, on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`on_fail`** *(str, Callable):* The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.

</ul>

<br/>

**`__call__(self, value, metadata={}) → ValidationResult`**

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
