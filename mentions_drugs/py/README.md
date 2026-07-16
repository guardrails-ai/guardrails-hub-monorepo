# guardrails-ai-mentions-drugs

Validates that the generated text does not contain any drug names

## Installation

```bash
pip install guardrails-ai-mentions-drugs
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.mentions_drugs import MentionsDrugs

guard = Guard().use(MentionsDrugs)
```

## License

MIT — © Guardrails AI.
