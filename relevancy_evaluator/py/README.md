# guardrails-ai-relevancy-evaluator

Validates that the reference text contains information relevant to answering the original question.

## Installation

```bash
pip install guardrails-ai-relevancy-evaluator
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.relevancy_evaluator import RelevancyEvaluator

guard = Guard().use(RelevancyEvaluator)
```

## License

MIT — © Guardrails AI.
