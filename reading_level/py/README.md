# guardrails-ai-reading-level

Parses text to find its readability as a US grade level number (0-12).

## Installation

```bash
pip install guardrails-ai-reading-level
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.reading_level import ReadingLevel

guard = Guard().use(ReadingLevel)
```

## License

MIT — © Guardrails AI.
