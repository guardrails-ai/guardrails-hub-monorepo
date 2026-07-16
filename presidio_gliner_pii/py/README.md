# guardrails-ai-presidio-gliner-pii

Detects personally identifiable information (PII) in text.

## Installation

```bash
pip install guardrails-ai-presidio-gliner-pii
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.presidio_gliner_pii.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.presidio_gliner_pii import PresidioGlinerPII

guard = Guard().use(PresidioGlinerPII)
```

## License

MIT — © Guardrails AI.
