# guardrails-ai-one-line

This validator checks if the input is a single line of text.

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
The validator ensures that a generated output is a single line based on whether the output has a newline character.

### Requirements

* Dependencies:
    - guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-one-line
```

## Usage Examples

### Validating string output via Python

In this example, we’ll test that a generated LLM sentence is a single line.

```python
# Import Guard and Validator
from guardrails_ai.one_line import OneLine
from guardrails import Guard

# Use the Guard with the validator
guard = Guard().use(OneLine, on_fail="exception")

# Test passing response
guard.validate(
    "Christopher Nolan's Tenet is a mind-bending action thriller that will keep you on the edge of your seat. The film is a must-watch for all Nolan fans."
)

try:
    # Test failing response
    guard.validate(
        "Christopher Nolan's Tenet is a mind-bending action thriller that will keep you on the edge of your seat\n. The film is a must-watch for all Nolan fans\n. Dunkirk was a great movie too."
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value Christopher Nolan's Tenet is a mind-bending action thriller that will keep you on the edge of your seat
. The film is a must-watch for all Nolan fans
. Dunkirk was a great movie too. is not a single line.
```

### Validating JSON output via Python

In this example, we verify that a summary of a product contains a single line.

```python
# Import Guard and Validator
from pydantic import BaseModel, Field
from guardrails_ai.one_line import OneLine
from guardrails import Guard

# Initialize Validator
val = OneLine(on_fail="exception")

# Create Pydantic BaseModel
class ProductInfo(BaseModel):
    product_name: str = Field(description="Name of the product")
    product_summary: str = Field(
        description="A one line summary of the product", validators=[val]
    )

# Create a Guard to check for valid Pydantic output
guard = Guard.from_pydantic(output_class=ProductInfo)

# Passing response
guard.parse(
    """
    {
        "product_name": "Hairspray",
        "product_summary": "This product helps your styled hair stay in place."
    }
    """
)

# Failing response
try:
    # Run LLM output generating JSON through guard
    guard.parse(
        """
        {
            "product_name": "Hairspray",
            "product_summary": "This product helps your styled hair stay in place\n. It is a very good product."
        }
        """
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value This product helps your styled hair stay in place
. It is a very good product. is not a single line.
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
