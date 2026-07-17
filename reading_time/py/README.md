# guardrails-ai-reading-time

Ensures that any generated text is less than a maximum expected reading time.

## Installation

```bash
pip install guardrails-ai-reading-time
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.reading_time import ReadingTime

guard = Guard().use(ReadingTime)
```

## License

MIT — © Guardrails AI.
