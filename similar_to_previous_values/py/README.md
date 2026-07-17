# guardrails-ai-similar-to-previous-values

Checks if a value is similar to a list of previously known correct values.

## Installation

```bash
pip install guardrails-ai-similar-to-previous-values
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.similar_to_previous_values.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.similar_to_previous_values import SimilarToPreviousValues

guard = Guard().use(SimilarToPreviousValues)
```

## License

MIT — © Guardrails AI.
