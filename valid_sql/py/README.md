# guardrails-ai-valid-sql

Validates whether the given SQL code is syntactically correct using. Optionally accepts a database schema to validate against using SQLAlchemy.

## Installation

```bash
pip install guardrails-ai-valid-sql
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.valid_sql import ValidSQL

guard = Guard().use(ValidSQL)
```

## License

MIT — © Guardrails AI.
