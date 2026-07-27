# guardrails-ai-nsfw-text

A Guardrails AI validator to detect NSFW text

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
This validator checks if an LLM-generated text is not safe for work (NSFW). It validates both sentence-by-sentence and the entire text.

### Requirements

* Dependencies:
    - guardrails-ai>=0.4.0   
    - nltk
    - transformers
    - torch

## Installation

```bash
pip install guardrails-ai-nsfw-text
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.nsfw_text.post_install
```

## Usage Examples

### Validating string output via Python

In this example, we use the `nsfw_text` validator on any LLM generated text.

```python
# Import Guard and Validator
from guardrails_ai.nsfw_text import NSFWText
from guardrails import Guard

# Setup Guard with the validator
guard = Guard().use(
    NSFWText, threshold=0.8, validation_method="sentence", on_fail="exception"
)

# Test passing response
guard.validate(
    "Christopher Nolan's Tenet is a mind-bending action thriller that will keep you on the edge of your seat. The film is a must-watch for all Nolan fans."
)

try:
    # Test failing response
    guard.validate(
        "Climate Change is real and we need to do something about it. Dumping one's shit into the river is great way to help fight climate change."
    )
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors: The following sentences in your response were found to be NSFW:

- Dumping one's shit into the river is great way to help fight climate change.
```

## API Reference

**`__init__(self, threshold=0.8, validation_method="sentence", on_fail="noop")`**
<ul>
Initializes a new instance of the Validator class.

**Parameters**
- **`threshold`** *(float)*: The confidence threshold over which model inferences are considered. Default is 0.8.
- **`validation_method`** *(str)*: The method to use for validation. If `sentence`, the validator will validate each sentence in the input text. If `full`, the validator will validate the entire input text. Default is `sentence`.
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
