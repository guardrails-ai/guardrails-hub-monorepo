# guardrails-ai-valid-range

Assess whether a generated number is between a maximum and minimum value.

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
This validator checks to see if a given numerical output is within an expected range.

### Requirements

* Dependencies:
    - guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-valid-range
```

## Usage Examples

### Validating JSON output via Python

In this example, we’ll use the validator to check that a field of a JSON output is within an expected range.

```python
# Import Guard and Validator
from pydantic import BaseModel, Field
from guardrails_ai.valid_range import ValidRange
from guardrails import Guard

# Initialize Validator
val = ValidRange(min=0, max=10, on_fail="exception")

# Create Pydantic BaseModel
class PetInfo(BaseModel):
    pet_name: str
    pet_age: int = Field(validators=[val])

# Create a Guard to check for valid Pydantic output
guard = Guard.from_pydantic(output_class=PetInfo)

# Run LLM output generating JSON through guard
guard.parse(
    """
    {
        "pet_name": "Caesar",
        "pet_age": 5
    }
    """
)

try:
    # Run LLM output generating JSON through guard
    guard.parse(
        """
        {
            "pet_name": "Caesar",
            "pet_age": 15
        }
        """
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value 15 is greater than 10.
```

## API Reference

**`__init__(self, min=None, max=None, on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`min`** _(int):_ The inclusive minimum value of the range.
- **`max`** _(int):_ The inclusive maximum value of the range.
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
