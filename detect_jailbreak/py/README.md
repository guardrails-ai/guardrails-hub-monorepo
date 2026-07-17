# guardrails-ai-detect-jailbreak

Detects attempts to circumvent safeguards in model conditioning.

## Installation

```bash
pip install guardrails-ai-detect-jailbreak
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.detect_jailbreak.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.detect_jailbreak import DetectJailbreak

guard = Guard().use(DetectJailbreak)
```

## License

MIT — © Guardrails AI.
