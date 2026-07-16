# guardrails-ai-prompt-injection-detector

A Guardrails validator that scores prompts for injection attempts via a secondary LLM.

## Installation

```bash
pip install guardrails-ai-prompt-injection-detector
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.prompt_injection_detector import PromptInjectionDetector

guard = Guard().use(PromptInjectionDetector)
```

## License

MIT — © Guardrails AI.
