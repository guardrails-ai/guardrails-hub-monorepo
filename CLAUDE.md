# CLAUDE.md

Guidance for working in this repo. It's a **public** monorepo of Guardrails-AI-owned
validators, published to public PyPI as `guardrails-ai-<name>` and importable from the
PEP 420 `guardrails_ai` namespace. See [README.md](./README.md) for the high-level
layout and [VALIDATORS.md](./VALIDATORS.md) for the catalog.

## Repo conventions

- **Public repo** — never commit secrets, personal emails, internal hostnames, private
  registry URLs (e.g. `pypi.guardrailsai.com`), or private hub-backend content. Author
  fields are normalized to `{name = "Guardrails AI"}` (no emails).
- Each validator is a **self-contained package** at `<name>/py/`; they version and
  publish independently.
- **Dist name** `guardrails-ai-<name>` (dashes); **import** `guardrails_ai.<name>`
  (underscores); **registered name** `guardrails/<name>` — the registered name must
  never change, or existing user guards break.
- Everything is **MIT** and may depend only on permissively licensed packages
  (enforced by the license sweep in CI).

## How to build a validator

A validator is a small package. To add one, create `<name>/py/` mirroring an existing
simple validator like `ban_list/py/`. The anatomy:

```
<name>/py/
├── pyproject.toml                       # name = guardrails-ai-<name>, license = MIT
├── Makefile                             # install / lint / type / test / license-check
├── README.md                            # install + usage
├── LICENSE                              # MIT
├── pyrightconfig.json, .coveragerc
├── requirements.lock                    # fully-resolved runtime deps (see below)
├── src/guardrails_ai/<name>/
│   ├── __init__.py                      # re-exports the validator class
│   └── main.py                          # the validator implementation
└── tests/
    ├── __init__.py
    └── test_main.py                     # standard test filename
```

### 1. The validator class (`src/guardrails_ai/<name>/main.py`)

Subclass `Validator`, decorate with `@register_validator`, and implement `validate()`:

```python
from typing import Any, Callable, Dict, Optional
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
    ErrorSpan,          # optional: for highlighting the offending text
)


@register_validator(name="guardrails/my_validator", data_type="string")
class MyValidator(Validator):
    """One-line summary, followed by a **Key Properties** table and Args docs.

    Args:
        threshold (float): ...
    """  # noqa

    def __init__(self, threshold: float = 0.5, on_fail: Optional[Callable] = None):
        # Pass every init arg to super().__init__ so it is serialized with the guard.
        super().__init__(threshold=threshold, on_fail=on_fail)
        self._threshold = threshold

    def validate(self, value: Any, metadata: Dict = {}) -> ValidationResult:
        if is_bad(value):
            return FailResult(
                error_message="Why it failed",
                fix_value=cleaned(value),          # optional programmatic fix
                error_spans=[ErrorSpan(start=0, end=3, reason="...")],  # optional
            )
        return PassResult()
```

Key rules:
- **`name="guardrails/<name>"`** must match the existing registered name — pick a new
  unique one for a brand-new validator and never rename it afterward.
- Forward **all** constructor args to `super().__init__(...)` — that's how the guard
  serializes/reconstructs the validator.
- Return `PassResult()` or `FailResult(...)`; `fix_value` and `error_spans` are optional.

`__init__.py` just re-exports:

```python
from .main import MyValidator

__all__ = ["MyValidator"]
```

### 2. `pyproject.toml`

Copy from `ban_list/py/pyproject.toml` and change name/description/dependencies. Keep:
- `license = "MIT"`, `authors = [{name = "Guardrails AI"}]` (no email),
- `requires-python = ">= 3.10,<4"`,
- runtime `dependencies` including `guardrails-ai>=0.4.0`,
- the `dev` optional-deps, `[build-system]`, `[tool.setuptools.packages.find] where = ["src"]`,
- the three `[project.urls]` (Homepage / Repository / Documentation) pointing at
  `guardrails-hub-monorepo/.../<name>/py`.
- **Depend on sibling validators via pip** (a normal PyPI dependency) — never via the
  deprecated `guardrails hub install`.

### 3. Tests

Put pytest tests in `tests/test_main.py` (this filename is the convention across the
repo). Exercise the validator through a real `Guard`:

```python
from guardrails import Guard
from guardrails_ai.my_validator import MyValidator
```

### 4. Register it in the catalog

Add an entry to [VALIDATORS.md](./VALIDATORS.md) under the appropriate risk category:
`- **Display Name** ([`guardrails-ai-<name>`](https://pypi.org/project/guardrails-ai-<name>/)): description.`

### 5. Lockfile

Generate the runtime dependency lock (universal, Python 3.10–3.13):

```bash
./scripts/generate_locks.sh        # regenerates all locks with uv
```

A package whose dependency isn't yet on public PyPI can't be locked yet (e.g.
`sensitive_topics` → `guardrails-ai-restricttotopic`); that's expected and documented.

## Per-package commands

Run from `<name>/py` in a virtualenv:

```bash
make install-dev      # pip install -e ".[dev]"
make lint             # ruff check + format --check
make lint-fix         # ruff --fix + format
make type             # pyright
make test             # pytest ./tests
make test-cov         # pytest with coverage xml
make license-check    # every resolved dep must be permissively licensed
```

## Versioning & publishing

- Versions are **per-package** and independent. Bump the `version` in that package's
  `pyproject.toml` when you change it. Prefer **minor** bumps for feature-level changes;
  never lower a version below what's already on PyPI (publish is guarded and would fail).
- On merge to `main`, `validators_publish.yml` change-detects each `<name>/py` whose
  version isn't yet tagged, publishes to PyPI via OIDC trusted publishing (no tokens),
  and tags `<name>-py-<version>`.

## CI gates (must pass before merge)

`validators_pr_qc.yml` runs a change-detected `{validator} × {py 3.10–3.13}` matrix:
install → lint → type → test → license sweep. Only changed `*/py/**` packages run.
