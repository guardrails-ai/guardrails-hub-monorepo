# guardrails-ai-detect-system-prompt-leakage

Detects system prompt leakage using fuzzy string matching (via `rapidfuzz`) to compare the LLM's response against a provided system prompt

## Installation

```bash
pip install guardrails-ai-detect-system-prompt-leakage
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.detect_system_prompt_leakage import DetectSystemPromptLeakage

guard = Guard().use(DetectSystemPromptLeakage)
```

## License

MIT — © Guardrails AI.
