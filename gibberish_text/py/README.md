# guardrails-ai-gibberish-text

A Guardrails AI validator to detect gibberish text.

## Installation

```bash
pip install guardrails-ai-gibberish-text
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.gibberish_text.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.gibberish_text import GibberishText

guard = Guard().use(GibberishText)
```

## License

MIT — © Guardrails AI.
