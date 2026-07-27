# guardrails-ai-mentions-drugs

Validates that the generated text does not contain any drug names

## Overview

| Developed by | Cartesia AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog |  |
| License | MIT |
| Input/Output | Output |

## Description

### Intended Use
This validator checks if an LLM-generated text contains names of any drugs. It uses a pre-specified list of drug names to check for matches in the input text. If a match is found, the validator fails.

### Requirements

* Dependencies:
    - guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-mentions-drugs
```

## Usage Examples

### Validating string output via Python

In this example, we use the `mentions_drugs` validator on any LLM generated text.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.mentions_drugs import MentionsDrugs

# Setup the Guard with the validator
guard = Guard().use(MentionsDrugs, on_fail="exception")

# Test passing response
guard.validate("You should take this medicine every day after breakfast.")

# Test failing response
try:
    response = guard.validate(
        "Take one dose of aspirin each night before going to sleep."
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: The generated text contains a drug name.
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
