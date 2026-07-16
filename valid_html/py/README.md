# guardrails-ai-valid-html

Guardrails validator that checks for HTML parseability.

## Installation

```bash
pip install guardrails-ai-valid-html
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.valid_html import ValidHtml

guard = Guard().use(ValidHtml)
```

## License

MIT — © Guardrails AI.
