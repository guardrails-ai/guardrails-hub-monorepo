# guardrails-ai-valid-address

Verifies an LLM-generated address using Google Maps' Address Validation API.

## Installation

```bash
pip install guardrails-ai-valid-address
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.valid_address import ValidAddress

guard = Guard().use(ValidAddress)
```

## License

MIT — © Guardrails AI.
