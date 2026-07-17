# guardrails-ai-detect-prompt-injection

Finds prompt injection using the Rebuff prompt library.

## Installation

```bash
pip install guardrails-ai-detect-prompt-injection
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.detect_prompt_injection import DetectPromptInjection

guard = Guard().use(DetectPromptInjection)
```

## License

MIT — © Guardrails AI.
