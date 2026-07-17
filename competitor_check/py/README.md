# guardrails-ai-competitor-check

Flags mentions of competitors. Fixes responses by filtering out competitor names.

## Installation

```bash
pip install guardrails-ai-competitor-check
```

This validator ships local models. After installing, run the post-install step to download them:

```bash
python -m guardrails_ai.competitor_check.post_install
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.competitor_check import CompetitorCheck

guard = Guard().use(CompetitorCheck)
```

## License

MIT — © Guardrails AI.
