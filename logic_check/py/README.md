# guardrails-ai-logic-check

Validates logical consistency and detects logical fallacies in the model output. Attempts to correct logical fallacies if found.

## Installation

```bash
pip install guardrails-ai-logic-check
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.logic_check import LogicCheck

guard = Guard().use(LogicCheck)
```

## License

MIT — © Guardrails AI.
