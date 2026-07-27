# guardrails-ai-valid-sql

Validates whether the given SQL code is syntactically correct using. Optionally accepts a database schema to validate against using SQLAlchemy.

## Overview

| Developed by | Guardrails AI |
| --- | --- |
| Date of development | Feb 15, 2024 |
| Validator type | Format |
| Blog |  |
| License | MIT |
| Input/Output | Output |

## Description

### Intended Use
This validator checks if a string follows valid SQL code. In order to do this, it expects either a `conn` string or a `schema` file. It checks the validity of generated SQL by performing the following steps:

1. If given a connection string, it connects to the DB instance.
2. Alternatively, if given a schema, it creates a local instance of the database based on the schema and connects to the local DB.
3. If neither a connection string nor schema is provided, then SQL validation is performed using `sqlvalidator` package.
4. In order to validate any generated LLM string representing a SQL statement, that statement is executed against the connected DB. If the statement runs without raising an exception, then the validator passes.

### Requirements

* Dependencies:
	- guardrails-ai>=0.4.0

## Installation

```bash
pip install guardrails-ai-valid-sql
```

## Usage Examples

### Validating string output via Python

In this example, we validate a generated SQL code by providing it with a schema file.

```python
# Import Guard and Validator
from guardrails import Guard
from guardrails_ai.valid_sql import ValidSQL

# Setup Guard
guard = Guard().use(
    ValidSQL, on_fail="exception"
)
response = guard.validate("SELECT * FROM EMPLOYEES;")  # Validator passes

try:
    response = guard.validate("SELEKT ID FROM USERS;")  # Validator fails
except Exception as e:
    print(e)
```
Output:
```console
Validation failed for field with errors:
```

## API Reference

**`__init__(self, conn=None, schema=None, on_fail="noop")`**
<ul>
Initializes a new instance of the Validator class.

**Parameters**
- **`conn`** *(str)*: The connection string to connect to a sql schema. E.g. `sqlite://`
- **`schema`** *(str)*: The `.sql` file representing the DB schema.
- **`on_fail`** *(str, Callable)*: The policy to enact when a validator fails. If `str`, must be one of `reask`, `fix`, `filter`, `refrain`, `noop`, `exception` or `fix_reask`. Otherwise, must be a function that is called when the validator fails.

</ul>
<br/>

**`__call__(self, value, metadata={}) -> ValidationResult`**
<ul>
Validates the given `value` using the rules defined in this validator, relying on the `metadata` provided to customize the validation process. This method is automatically invoked by `guard.parse(...)`, ensuring the validation logic is applied to the input data.

Note:

1. This method should not be called directly by the user. Instead, invoke `guard.parse(...)` where this method will be called internally for each associated Validator.
2. When invoking `guard.parse(...)`, ensure to pass the appropriate `metadata` dictionary that includes keys and values required by this validator. If `guard` is associated with multiple validators, combine all necessary metadata into a single dictionary.

**Parameters**
- **`value`** *(Any)*: The input value to validate.
- **`metadata`** *(dict)*: A dictionary containing metadata required for validation. For this validator, no additional metadata keys are required.

</ul>

## License

MIT — © Guardrails AI.
