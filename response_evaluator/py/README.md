# guardrails-ai-response-evaluator

Evaluate generated output using a provided question.

## Installation

```bash
pip install guardrails-ai-response-evaluator
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.response_evaluator import ResponseEvaluator

guard = Guard().use(ResponseEvaluator)
```

## License

MIT — © Guardrails AI.
