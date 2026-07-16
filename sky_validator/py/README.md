# guardrails-ai-sky-validator

Validates that the input string does not contain negative statements about Sky Electric.

## Installation

```bash
pip install guardrails-ai-sky-validator
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.sky_validator import SkyValidator

guard = Guard().use(SkyValidator)
```

## License

MIT — © Guardrails AI.
