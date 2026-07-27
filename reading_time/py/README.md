# guardrails-ai-reading-time

Ensures that any generated text is less than a maximum expected reading time.

## Overview

| Developed by | Guardrails AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog | - |
| License | MIT |
| Input/Output | Output |

## Description

### Intended Use
This validator ensures that any LLM generated text is readable within an expected reading time. The reading time estimation is done at 200 words / min.

### Requirements

* Dependencies:
    - guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-reading-time
```

## Usage Examples

### Validating string output via Python

In this example, we’ll use the validator to validate that an LLM description is under 5 seconds of reading time.

```python
# Import Guard and Validator
from guardrails_ai.reading_time import ReadingTime
from guardrails import Guard

FIVE_SECONDS = 5 / 60
# Use the Guard with the validator
guard = Guard().use(ReadingTime, reading_time=FIVE_SECONDS, on_fail="exception")

# Test passing response
guard.validate("Azure is a cloud computing service created by Microsoft.")

try:
    # Test failing response
    guard.validate(
        """
        Azure is a cloud computing service created by Microsoft. It was first announced in 2008 and 
        released in 2010. It is a cloud computing service that provides a range of services, 
        including those for compute, analytics, storage, and networking. 
        It can be used to build, deploy, and manage applications and services.
        """
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: String should be readable within 0.083 min. but took 0.255 min. to read.
```

## API Reference

**`__init__(self, reading_time, on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`reading_time`** _(float):_ The maximum reading time in minutes.
- **`on_fail`** *(str, Callable):* The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.

</ul>

<br/>

**`__call__(self, value, metadata={}) -> ValidationResult`**

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
