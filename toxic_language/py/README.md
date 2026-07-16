# guardrails-ai-toxic-language

Identifies and flags toxic language in text to ensure communications remain professional and appropriate.

## Installation

```bash
pip install guardrails-ai-toxic-language
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.toxic_language.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.toxic_language import ToxicLanguage

guard = Guard().use(ToxicLanguage)
```

## License

MIT — © Guardrails AI.
