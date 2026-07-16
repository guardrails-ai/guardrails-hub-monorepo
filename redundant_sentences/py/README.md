# guardrails-ai-redundant-sentences

Identifies redundant sentences in text using fuzzy matching.

## Installation

```bash
pip install guardrails-ai-redundant-sentences
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.redundant_sentences import RedundantSentences

guard = Guard().use(RedundantSentences)
```

## License

MIT — © Guardrails AI.
