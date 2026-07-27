# guardrails-ai-valid-open-api-spec

Ensures that a generated output is a valid OpenAPI Specification.

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
This validator ensures that a generated output is a valid OpenAPI Specification.

### Requirements

* Dependencies:
	- guardrails-ai>=0.4.0
  - jsonschema
  - pyyaml
  - referencing

## Installation

```bash
pip install guardrails-ai-valid-open-api-spec
```

## Usage Examples

### Validating string output via Python

In this example, we’ll test that a generated value is a valid OpenAPI spec.

```python
import json
# Import Guard and Validator
from guardrails_ai.valid_open_api_spec import ValidOpenApiSpec
from guardrails import Guard

# Setup Guard
guard = Guard().use(
  ValidOpenApiSpec, on_fail="exception"
)

guard.validate(
    json.dumps(
        {"openapi": "3.0.0", "info": {"title": "API", "version": "1.0.0"}, "paths": {}}
    )
)  # Validator passes

try:
    guard.validate(
        json.dumps({"openapi": "3.0.0", "info": {"title": "API"}})
    )  # Validator fails; note the missing version
except Exception as e:
    print(e)  # Raises an exception
```
Output:
```console
Validation failed for field with errors: Value is not a valid OpenAPI Specification.
The following fields are invalid:
{
  "$": [
    "'paths' is a required property"
  ],
  "$.info": [
    "'version' is a required property"
  ]
}
```

## API Reference

**`__init__(self, on_fail="noop")`**
<ul>
Initializes a new instance of the Validator class.

**Parameters**
- **`on_fail`** *(str, Callable)*: The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
</ul>
<br/>

**`__call__(self, value, metadata={}) -> ValidationOutcome`**
<ul>
Validates the given `value` using the rules defined in this validator, relying on the `metadata` provided to customize the validation process. This method is automatically invoked by `guard.parse(...)`, ensuring the validation logic is applied to the input data.

Note:

1. This method should not be called directly by the user. Instead, invoke `guard.parse(...)` where this method will be called internally for each associated Validator.
2. When invoking `guard.parse(...)`, ensure to pass the appropriate `metadata` dictionary that includes keys and values required by this validator. If `guard` is associated with multiple validators, combine all necessary metadata into a single dictionary.

**Parameters**
- **`value`** *(Any)*: The input value to validate.
- **`metadata`** *(dict)*: A dictionary containing metadata required for validation. No additional metadata keys are needed for this validator.

</ul>

## License

MIT — © Guardrails AI.
