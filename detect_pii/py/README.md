# guardrails-ai-detect-pii

Detects personally identifiable information (PII) in text, using Microsoft Presidio.

## Installation

```bash
pip install guardrails-ai-detect-pii
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.detect_pii.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.detect_pii import DetectPII

guard = Guard().use(DetectPII)
```

## License

MIT — © Guardrails AI.
