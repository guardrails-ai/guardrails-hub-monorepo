# guardrails-ai-contains-string

A Guardrails AI validator to check if the LLM-generated text contains a substring.

## Overview
| Developed by | Guardrails AI |
| --- | --- |
| Date of development | Apr 24, 2024 |
| Validator type | Format |
| Blog | - |
| License | MIT |
| Input/Output | Output |

## Description

This validator ensures that a string contains a substring.

## Installation

```bash
pip install guardrails-ai-contains-string
```

## Usage Examples
### Validating string output via Python

In this example, we'll test that a generated word contains the substring `s`.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.contains_string import ContainsString

# Setup Guard with the validator
guard = Guard().use(ContainsString, substring="s", on_fail="exception")

# Test passing string
guard.validate("pass")

# Test failing string
try:
    guard.validate("fail")
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: fail doesn't contain s
```

## API Reference

**`__init__(self, substring: str, on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`substring`** *(str):* The substring that the input string is expected to contain.
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
