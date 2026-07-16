# guardrails-ai-llm-critic

Grade the generated response based on provided criteria.

## Installation

```bash
pip install guardrails-ai-llm-critic
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.llm_critic import LLMCritic

guard = Guard().use(LLMCritic)
```

## License

MIT — © Guardrails AI.
