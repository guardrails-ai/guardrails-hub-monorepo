# guardrails-ai-responsiveness-check

Ensure generated output is polite.

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
This validator ensures that a generated output responds to the given prompt.

### Requirements

* Dependencies:
    - `litellm`
    - guardrails-ai>=0.4.0

* API keys: Set your LLM provider API key as an environment variable which will be used by `litellm` to authenticate with the LLM provider. For more information on supported LLM providers and how to set up the API key, refer to the LiteLLM documentation.

## Installation

```bash
pip install guardrails-ai-responsiveness-check
```

## Usage Examples

### Validating string output via Python

In this example, we’ll test that a generated output actually answers the question posed in the prompt.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.responsiveness_check import ResponsivenessCheck

# Setup Guard
guard = Guard().use(
    ResponsivenessCheck,
    llm_callable="gpt-3.5-turbo",
    on_fail="exception",
)

res = guard.validate(
    "Jefferson City is the capital of Missouri.", 
    metadata={
        "original_prompt": "What is the capital of Missouri?",
        "pass_on_invalid": True
    }
)  # Validation passes
try:
    res = guard.validate(
        "Berlin is the capital of Germany.",
        metadata={
            "original_prompt": "What is the capital of Missouri?",
        }
    )  # Validation fails because this response isn't related to what we asked.
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: The LLM says 'No'. The validation failed.
```

## API Reference

**`__init__(self, prompt, llm_callable='gpt-3.5-turbo', on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`prompt`** *(str):* The original prompt to the LLM.
- **`llm_callable`** *(str):* Model name to make the LiteLLM call. Defaults to `gpt-3.5-turbo`.
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
- **`metadata`** *(dict):* A dictionary containing metadata required for validation. Keys and values must match the expectations of this validator.
    
    
    | Key | Type | Description | Default | Required |
    | --- | --- | --- | --- | --- |
    | `original_prompt` | String | The original prompt to the LLM | - | Yes |
    | `pass_on_invalid` | Boolean | Whether to pass the validation if the LLM returns an invalid response | False | No |

</ul>

## License

MIT — © Guardrails AI.
