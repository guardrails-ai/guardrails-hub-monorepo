# guardrails-ai-web-sanitization

Scans LLM outputs for strings that could cause browser script execution downstream.

## Installation

```bash
pip install guardrails-ai-web-sanitization
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.web_sanitization import WebSanitization

guard = Guard().use(WebSanitization)
```

## License

MIT — © Guardrails AI.
