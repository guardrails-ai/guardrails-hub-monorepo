# guardrails-ai-regex-match

Ensure content matches a provided regular expression. This can be used to validate content such as email addresses, phone numbers, and more.

## Installation

```bash
pip install guardrails-ai-regex-match
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.regex_match import RegexMatch

guard = Guard().use(RegexMatch)
```

## License

MIT — © Guardrails AI.
