# guardrails-ai-nsfw-text

A Guardrails AI validator to detect NSFW text

## Installation

```bash
pip install guardrails-ai-nsfw-text
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.nsfw_text.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.nsfw_text import NSFWText

guard = Guard().use(NSFWText)
```

## License

MIT — © Guardrails AI.
