# guardrails-ai-bias-check

Validates that the text is free from biases related to age, gender, sex, ethnicity, religion, etc.

## Installation

```bash
pip install guardrails-ai-bias-check
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.bias_check.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.bias_check import BiasCheck

guard = Guard().use(BiasCheck)
```

## License

MIT — © Guardrails AI.
