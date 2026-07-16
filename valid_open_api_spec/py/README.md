# guardrails-ai-valid-open-api-spec

Ensures that a generated output is a valid OpenAPI Specification.

## Installation

```bash
pip install guardrails-ai-valid-open-api-spec
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.valid_open_api_spec import ValidOpenApiSpec

guard = Guard().use(ValidOpenApiSpec)
```

## License

MIT — © Guardrails AI.
