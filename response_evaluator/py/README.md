# guardrails-ai-response-evaluator

Evaluate generated output using a provided question.

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
This validator validates an LLM response based on a question provided by the user. The user-provided (rhetorical) question is expected to fact-check or ask the LLM whether the response is correct. If the LLM returns 'Yes' or 'No', the validator will pass or fail accordingly. If the LLM returns an invalid response, the validator will pass if the `pass_on_inavlid` flag is set to `True` in the metadata.

### Requirements

* Dependencies:
    - `litellm`
    - guardrails-ai>=0.4.0

* API keys: Set your LLM provider API key as an environment variable which will be used by `litellm` to authenticate with the LLM provider.

* For more information on supported LLM providers and how to set up the API key, refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/).
    
## Installation

```bash
pip install guardrails-ai-response-evaluator
```

## Usage Examples

### Validating string output via Python

In this example, we use the `response_evaluator` validator on any LLM generated text.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.response_evaluator import ResponseEvaluator

# Initialize The Guard with this validator
guard = Guard().use(
    ResponseEvaluator, llm_callable="gpt-3.5-turbo", on_fail="exception"
)

# Test passing response
guard.validate(
    "The capital of France is Paris",
    metadata={
        "validation_question": "Is Paris the capital of France?",
        "pass_on_invalid": True,
    },
)  # Pass

try:
    # Test failing response
    guard.validate(
        "The capital of France is London",
        metadata={
            "validation_question": "Is Paris the capital of France?",
        },
    )  # Fail
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: The LLM says 'No'. The validation failed.
```

## API Reference

**`__init__(self, llm_callable="gpt-3.5-turbo", on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`llm_callable`** *(str):* The string name for the model used with LiteLLM. More info about available options [here](https://docs.litellm.ai/docs/). Default is `gpt-3.5-turbo`.
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
    | `validation_question` | String | The question to ask the LLM | N/A | Yes |
    | `pass_on_invalid` | Boolean | Whether to pass the validation if the LLM returns an invalid response | False | No |

</ul>

## License

MIT — © Guardrails AI.
