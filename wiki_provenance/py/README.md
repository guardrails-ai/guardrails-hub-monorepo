# guardrails-ai-wiki-provenance

A Guardrails AI validator that detects and removes hallucinated text based off Wikipedia

## Installation

```bash
pip install guardrails-ai-wiki-provenance
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.wiki_provenance.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.wiki_provenance import WikiProvenance

guard = Guard().use(WikiProvenance)
```

## License

MIT — © Guardrails AI.
