# guardrails-ai-exclude-sql-predicates

This rule checks for the use of particular SQL predicates in the query. It is important to exclude SQL predicates from the query to prevent SQL injection attacks.

## Installation

```bash
pip install guardrails-ai-exclude-sql-predicates
```

## Usage

```python
from guardrails import Guard
from guardrails_ai.exclude_sql_predicates import ExcludeSqlPredicates

guard = Guard().use(ExcludeSqlPredicates)
```

## License

MIT — © Guardrails AI.
