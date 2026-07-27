# guardrails-ai-llm-critic

Grade the generated response based on provided criteria.

## Overview

| Developed by | Guardrails AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog |  |
| License | MIT |
| Input/Output | Output |
| Open-source contributor | [Alex Falconer-Athanassakos](https://github.com/alexf-a) |

## Description

### Intended Use

This validator validates an LLM response by grading the response against a set of provided metrics and criteria. If the evaluation for each criterion is above a certain threshold, the response is considered valid. Otherwise, the response is considered invalid.

### Requirements

* Dependencies:
    - `litellm`
    - guardrails-ai>=0.4.0

* API keys: Set your LLM provider API key as an environment variable which will be used by `litellm` to authenticate with the LLM provider.
For more information on supported LLM providers and how to set up the API key, refer to the [LiteLLM documentation](https://docs.litellm.ai/docs/).

## Installation

```bash
pip install guardrails-ai-llm-critic
```

## Usage Examples

### Validating string output via Python

In this example, we use the `llm_critic` validator on any LLM generated text.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.llm_critic import LLMCritic

# Initialize The Guard with this validator
guard = Guard().use(
    LLMCritic,
    metrics={
        "informative": {
            "description": "An informative summary captures the main points of the input and is free of irrelevant details.",
            "threshold": 75,
        },
        "coherent": {
            "description": "A coherent summary is logically organized and easy to follow.",
            "threshold": 50,
        },
        "concise": {
            "description": "A concise summary is free of unnecessary repetition and wordiness.",
            "threshold": 50,
        },
        "engaging": {
            "description": "An engaging summary is interesting and holds the reader's attention.",
            "threshold": 50,
        },
    },
    max_score=100,
    llm_callable="gpt-3.5-turbo-0125",
    on_fail="exception",
)

# Test passing response
guard.validate(
    """
    A judge has ordered former President Donald Trump to pay approximately $450 million to New York State in a civil
    fraud case, which could significantly impact his financial assets. The ruling also restricts Trump from running any
    New York company and obtaining loans from New York banks for a specified period. These measures are described as
    unprecedented threats to Trump's finances and may temporarily set back his real estate company. A court-appointed
    monitor will oversee the family business. Trump's lawyer criticized the ruling, while these penalties could
    foreshadow challenges he will face in upcoming criminal trials, which carry the potential for imprisonment.
    """,
)  # Pass

try:
    # Test failing response
    guard.validate(
        "Donald Trump was fined.",
    )  # Fail
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: The response failed the following metrics: ['informative', 'engaging'].
```

## API Reference

**`__init__(self, metrics={}, max_score=5, llm_callable="gpt-3.5-turbo", on_fail="noop")`**
<ul>

Initializes a new instance of the Validator class.

**Parameters:**

- **`metrics`** *(dict):* A dictionary containing the metrics to evaluate the LLM response. The keys are the names of the metrics, and the values are dictionaries containing the following keys:
    - `description` *(str):* A description of the metric.
    - `threshold` *(int):* The minimum score required for the response to pass the metric.
- **`max_score`** *(int):* The maximum score that can be achieved by the LLM response. Default is 5.
- **`llm_callable`** *(str):* The string name for the model used with LiteLLM. More info about available options [here](https://docs.litellm.ai/docs/). Default is `gpt-3.5-turbo`.
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
- **`metadata`** *(dict):* A dictionary containing metadata required for validation. No additional keys are required for this validator.

</ul>

## License

MIT — © Guardrails AI.
