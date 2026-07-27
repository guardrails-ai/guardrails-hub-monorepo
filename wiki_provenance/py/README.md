# guardrails-ai-wiki-provenance

A Guardrails AI validator that detects and removes hallucinated text based off Wikipedia

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
This validator checks if an LLM-generated text contains hallucinations. It retrieves the most relevant information from wikipedia and checks if the LLM-generated text is similar to the retrieved information using another LLM.

### Requirements

* Dependencies: 
    - guardrails-ai>=0.4.0  
    - litellm 
    - chromadb 
    - wikipedia 
    - nltk
    
* Note:
    - Create a single Guard object per `topic_name` to avoid redundant wikipedia and vector collections.

## Installation

```bash
pip install guardrails-ai-wiki-provenance
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.wiki_provenance.post_install
```

## Usage Examples

### Validating string output via Python

In this example, we use the `wiki_provenance` validator on any LLM generated text.

```python
# Import Guard and Validator
from guardrails_ai.wiki_provenance import WikiProvenance
from guardrails import Guard

# Use the Guard with the validator
guard = Guard().use(
    WikiProvenance,
    topic_name="Apple company",
    validation_method="sentence",
    llm_callable="gpt-3.5-turbo",
    on_fail="exception"
)

# Test passing response
guard.validate("Apple was founded by Steve Jobs in April 1976.", metadata={"pass_on_invalid": True})  # Pass

# Test failing response
try:
    guard.validate("Ratan Tata founded Apple in September 1998 as a fruit selling company.")  # Fail
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: None of the following sentences in the response are supported by the provided context:
- Ratan Tata founded Apple in September 1998 as a fruit selling company.
```

## API Reference

**`__init__(self, topic_name, validation_method='sentence', llm_callable='gpt-3.5-turbo', on_fail="noop")`**
<ul>
Initializes a new instance of the Validator class.

**Parameters**
- **`topic_name`** *(str)*: The name of the topic to search for in Wikipedia.
- **`validation_method`** *(str)*: The method to use for validating the input. Must be one of `sentence` or `full`. If `sentence`, the input is split into sentences and each sentence is validated separately. If `full`, the input is validated as a whole. Default is `sentence`.
- **`llm_callable`** *(str)*: The name of the LiteLLM model string to use for validating the input. Default is `gpt-3.5-turbo`.
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
- **`metadata`** *(dict)*: A dictionary containing metadata required for validation. Keys and values must match the expectations of this validator.
    
    
    | Key | Type | Description | Default | Required |
    | --- | --- | --- | --- | --- |
    | `pass_on_invalid` | Boolean | Whether to pass the validation if the LLM returns an invalid response | False | No |
</ul>

## License

MIT — © Guardrails AI.
