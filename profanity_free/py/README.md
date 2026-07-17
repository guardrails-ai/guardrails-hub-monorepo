# guardrails-ai-profanity-free

Checks for profanity in text, using the alt-profanity-check library.

## Installation

```bash
pip install guardrails-ai-profanity-free
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.profanity_free.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.profanity_free import ProfanityFree

guard = Guard().use(ProfanityFree)
```

## License

MIT — © Guardrails AI.
