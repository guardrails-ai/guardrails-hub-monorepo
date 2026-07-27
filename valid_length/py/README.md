# guardrails-ai-valid-length

Ensures the length of a string or list falls between a minimum and maximum.

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
This validator can perform the following checks:

1. If applying this validator on a string: ensures that a generated string is of an expected length
2. If applying this validator on a generated JSON object: ensures that a generated list is of an expected length

### Requirements

* Dependencies:
	- guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-valid-length
```

## Usage Examples

### Validating string output via Python

In this example, we verify that an LLM generated response contains anywhere from 3-6 characters.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.valid_length import ValidLength

# Setup Guard
guard = Guard().use(
    ValidLength, min=3, max=6, on_fail="exception"
)
response = guard.validate("hello")  # Validator passes

try:
    response = guard.validate("hello world!")  # Validator fails
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value has length greater than 6. Please return a shorter output, that is shorter than 6 characters.
```

### Validating the length of a list within a generated JSON

This example applies the validator to a list of a JSON object, and ensures that the length of the list is within an expected range.

```python
# Import Guard and Validator
from pydantic import BaseModel, Field
from guardrails_ai.valid_length import ValidLength
from guardrails import Guard

val = ValidLength(min=1, max=2, on_fail="exception")

# Create Pydantic BaseModels
class ProductInfo(BaseModel):
    """Information about a single product."""

    product_name: str = Field(description="Name of the product")
    product_summary: str = Field(description="A summary of the product")

class ProductCategory(BaseModel):
    """List of products."""

    category_name: str = Field(description="Name of product category")
    products: list[ProductInfo] = Field(
        description="List of products", validators=[val]
    )

# Create a Guard to check for valid Pydantic output
guard = Guard.from_pydantic(output_class=ProductCategory)

# Run LLM output generating JSON through guard
guard.parse(
    """
    {
        "category_name": "Hair care",
        "products": [
            {
                "product_name": "Hair spray",
                "product_summary": "Helps your styled hair stay in place."
            },
            {
                "product_name": "Shampoo",
                "product_summary": "Helps clean your hair."
            }
        ]
    """
)

try:
    # Run LLM output generating JSON through guard
    guard.parse(
        """
        {
            "category_name": "Hair care",
            "products": [
                {
                    "product_name": "Hair spray",
                    "product_summary": "Helps your styled hair stay in place."
                },
                {
                    "product_name": "Shampoo",
                    "product_summary": "Helps clean your hair."
                },
                {
                    "product_name": "Conditioner",
                    "product_summary": "Helps condition your hair."
                }
            ]
        }
        """
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: Value has length greater than 2. Please return a shorter output, that is shorter than 2 characters.
```

## API Reference

**`__init__(self, min=None, max=None, on_fail="noop")`**
<ul>
Initializes a new instance of the Validator class.

**Parameters**
- **`min`** *(int)*: Min expected length of the object (str, list).
- **`max`** *(int)*: Max expected length of the object (str, list).
- **`on_fail`** *(str, Callable)*: The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.
</ul>
<br/>

**`__call__(self, value, metadata={}) -> ValidationResult`**
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
