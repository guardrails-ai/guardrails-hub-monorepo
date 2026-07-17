# guardrails-ai-extracted-summary-sentences-match

This validator checks if the extracted summary sentences match the original document.

## Installation

```bash
pip install guardrails-ai-extracted-summary-sentences-match
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.extracted_summary_sentences_match import ExtractedSummarySentencesMatch

guard = Guard().use(ExtractedSummarySentencesMatch)
```

## License

MIT — © Guardrails AI.
