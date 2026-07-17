# guardrails-ai-similar-to-document

Checks if some generated text is similar to a provided document.

## Installation

```bash
pip install guardrails-ai-similar-to-document
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.similar_to_document import SimilarToDocument

guard = Guard().use(SimilarToDocument)
```

## License

MIT — © Guardrails AI.
