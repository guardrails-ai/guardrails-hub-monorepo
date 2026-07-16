# guardrails-ai-provenance-llm

A validator for ensuring the factuality and reducing brand risk in generated content.

## Installation

```bash
pip install guardrails-ai-provenance-llm
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.provenance_llm.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.provenance_llm import ProvenanceLLM

guard = Guard().use(ProvenanceLLM)
```

## License

MIT — © Guardrails AI.
