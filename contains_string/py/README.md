# guardrails-ai-contains-string

A Guardrails AI validator to check if the LLM-generated text contains a substring.

## Installation

```bash
pip install guardrails-ai-contains-string
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.contains_string import ContainsString

guard = Guard().use(ContainsString)
```

## License

MIT — © Guardrails AI.
