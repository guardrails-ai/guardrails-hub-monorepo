# guardrails-ai-endpoint-is-reachable

Checks if an endpoint can be reached by making a request to it.

## Installation

```bash
pip install guardrails-ai-endpoint-is-reachable
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.endpoint_is_reachable import EndpointIsReachable

guard = Guard().use(EndpointIsReachable)
```

## License

MIT — © Guardrails AI.
