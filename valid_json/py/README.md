# guardrails-ai-valid-json

Ensure content is parseable as valid JSON.

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
This validator ensures that a generated output is parseable as valid JSON.

### Requirements

* Dependencies:
    - guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-valid-json
```

## Usage Examples

### Validating string output via Python

In this example, we’ll test that a generated value is valid json.

```python
# Import Guard and Validator
from guardrails_ai.valid_json import ValidJson
from guardrails import Guard

# Setup Guard
guard = Guard().use(ValidJson, on_fail="exception")

guard.validate('{ "value": "a test value" }')  # Validator passes

try:
    guard.validate(
        '{ "value": "a test value", }'
    )  # Validator fails; note the trailing comma
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value is not parseable as valid JSON! Reason: Expecting property name enclosed in double quotes: line 1 column 28 (char 27)
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
