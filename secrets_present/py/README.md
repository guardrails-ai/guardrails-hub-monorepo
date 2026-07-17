# guardrails-ai-secrets-present

Detects the secrets present in text by matching against common patterns for API keys and other sensitive information.

## Installation

```bash
pip install guardrails-ai-secrets-present
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.secrets_present import SecretsPresent

guard = Guard().use(SecretsPresent)
```

## License

MIT — © Guardrails AI.
