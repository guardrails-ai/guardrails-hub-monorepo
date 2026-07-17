# guardrails-ai-qa-relevance-llm-eval

Makes a second request to the LLM, asking it if its original response was relevant to the prompt.

## Installation

```bash
pip install guardrails-ai-qa-relevance-llm-eval
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.qa_relevance_llm_eval import QARelevanceLLMEval

guard = Guard().use(QARelevanceLLMEval)
```

## License

MIT — © Guardrails AI.
