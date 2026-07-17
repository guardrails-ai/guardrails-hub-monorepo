# guardrails-ai-toxic-language-llm

Detects toxic language in LLM-generated text using an LLM as the detection backbone. Evaluates text across seven toxicity categories: toxicity, severe toxicity, obscene, threat, insult, identity attack, and sexual explicit content.

## Installation

```bash
pip install guardrails-ai-toxic-language-llm
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.toxic_language_llm import ToxicLanguageLLM

guard = Guard().use(ToxicLanguageLLM)
```

## License

MIT — © Guardrails AI.
