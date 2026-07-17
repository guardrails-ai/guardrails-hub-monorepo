# guardrails-ai-sensitive-topics

A Guardrails AI validator that detects sensitive topics in text.

## Installation

```bash
pip install guardrails-ai-sensitive-topics
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.sensitive_topics import SensitiveTopic

guard = Guard().use(SensitiveTopic)
```

## License

MIT — © Guardrails AI.
