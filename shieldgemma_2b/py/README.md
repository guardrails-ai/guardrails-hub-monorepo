# guardrails-ai-shieldgemma-2b

A Gemma based validator for moderating user prompts to guard against harmful content by specifying a policy.

## Installation

```bash
pip install guardrails-ai-shieldgemma-2b
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.shieldgemma_2b import ShieldGemma2B

guard = Guard().use(ShieldGemma2B)
```

## License

MIT — © Guardrails AI.
