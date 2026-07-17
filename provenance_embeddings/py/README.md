# guardrails-ai-provenance-embeddings

Compares embeddings of generated and source texts to calculate provenance.

## Installation

```bash
pip install guardrails-ai-provenance-embeddings
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.provenance_embeddings.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.provenance_embeddings import ProvenanceEmbeddings

guard = Guard().use(ProvenanceEmbeddings)
```

## License

MIT — © Guardrails AI.
