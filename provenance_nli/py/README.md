# guardrails-ai-provenance-nli

Detects and removes hallucinations from LLM-generated text using an NLI model to validate it against a provided context.

## Installation

```bash
pip install guardrails-ai-provenance-nli
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.provenance_nli.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.provenance_nli import ProvenanceNLI

guard = Guard().use(ProvenanceNLI)
```

## License

MIT — © Guardrails AI.
