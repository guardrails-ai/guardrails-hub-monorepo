# guardrails-ai-guardrails-pii

Detects personally identifiable information (PII) in text.

## Installation

```bash
pip install guardrails-ai-guardrails-pii
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.guardrails_pii.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.guardrails_pii import GuardrailsPII

guard = Guard().use(GuardrailsPII)
```

## License

MIT — © Guardrails AI.
