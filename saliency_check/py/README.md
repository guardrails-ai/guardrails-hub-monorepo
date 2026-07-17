# guardrails-ai-saliency-check

Checks if a generated summary covers topics present in a source document.

## Installation

```bash
pip install guardrails-ai-saliency-check
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.saliency_check import SaliencyCheck

guard = Guard().use(SaliencyCheck)
```

## License

MIT — © Guardrails AI.
