# guardrails-ai-llamaguard-7b

A llama based validator which checks whether a given prompt is safe/unsafe by specifying a set of  policies and lists the violating policies when applicable.

## Installation

```bash
pip install guardrails-ai-llamaguard-7b
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.llamaguard_7b import LlamaGuard7B

guard = Guard().use(LlamaGuard7B)
```

## License

MIT — © Guardrails AI.
