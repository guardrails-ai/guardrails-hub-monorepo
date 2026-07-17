# guardrails-ai-unusual-prompt

A Guardrails AI input validator that validates a prompt for unusualness and trickery.

## Installation

```bash
pip install guardrails-ai-unusual-prompt
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.unusual_prompt import UnusualPrompt

guard = Guard().use(UnusualPrompt)
```

## License

MIT — © Guardrails AI.
