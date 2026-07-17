# guardrails-ai-ban-list

Validates that the output does not contain banned words, using fuzzy search.

## Installation

```bash
pip install guardrails-ai-ban-list
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.ban_list import BanList

guard = Guard().use(BanList)
```

## License

MIT — © Guardrails AI.
