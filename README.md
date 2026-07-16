# Guardrails Hub Monorepo

Monorepo for Guardrails-AI-owned **validators**, published to public PyPI as
`guardrails-ai-<name>` and importable from the PEP 420 `guardrails_ai` namespace.

```bash
pip install guardrails-ai-detect-pii
```

```python
from guardrails import Guard
from guardrails_ai.detect_pii import DetectPII

guard = Guard().use(DetectPII)
```

See **[VALIDATORS.md](./VALIDATORS.md)** for the full catalog, grouped by risk category.

## Layout

Each validator is a self-contained package at the repo root:

```
<name>/
└── py/
    ├── pyproject.toml            # name = guardrails-ai-<name>, license = MIT
    ├── Makefile                  # install / lint / type / test / license-check
    ├── pyrightconfig.json, .coveragerc, LICENSE (MIT), README.md
    ├── src/guardrails_ai/<name>/ # importable as guardrails_ai.<name> (PEP 420, no __init__ at namespace root)
    └── tests/
```

- **Dist name:** `guardrails-ai-<name>` (underscores → dashes).
- **Import:** `from guardrails_ai.<name> import <Export>`.
- **Registered validator name is unchanged:** `@register_validator(name="guardrails/<name>")`,
  so existing guards keep working.
- **Versioning:** independent per package; a release is gated by the git tag `<name>-py-<version>`.

## Developing a validator

From `<name>/py` in a fresh virtual environment:

```bash
python -m venv .venv && . .venv/bin/activate
make install install-dev
make lint             # ruff
make type             # pyright
make test             # pytest ./tests
make license-check    # license sweep (MIT-only dependency trees)
```

## Adding a validator

Create a new `<name>/py/` package following the layout above: an MIT-licensed
`pyproject.toml` named `guardrails-ai-<name>`, source under `src/guardrails_ai/<name>/`,
and tests. CI picks it up automatically via the `*/py/**` path filters.

## Dependency locks

Each package pins its fully resolved dependency tree in `py/requirements.lock`
for reproducible installs — **universal** locks, valid across platforms and
Python 3.10-3.13. `sensitive_topics` has no lock yet: it depends on
`guardrails-ai-restricttotopic`, which is not yet on PyPI, so its lock will
generate once that package is published.

Regenerate them with [uv](https://docs.astral.sh/uv/):

```bash
./scripts/generate_locks.sh
```

## Licensing

Every validator package is **MIT** and must depend only on permissively licensed
packages. The merge-blocking license sweep (`make license-check`, wired into
`validators_pr_qc.yml`) reads the allowlist in
[`.licenses-allow.txt`](./.licenses-allow.txt) and the documented, manually
reviewed exceptions in [`.licenses-exceptions.txt`](./.licenses-exceptions.txt).

## CI

- **`.github/workflows/validators_pr_qc.yml`** — change-detected matrix
  (`{changed validator} × {py 3.10–3.13}`): install, lint, type, tests, license sweep.
- **`.github/workflows/validators_publish.yml`** — change-detected trusted publishing
  to public PyPI via OIDC (no tokens), with a version-bump guard and git tagging.
- **`.github/workflows/bootstrap_publish.yml`** — one-time token-auth publish that
  creates the PyPI projects, before per-project trusted publishers are bound.
- **`.github/dependabot.yml`** — weekly `pip` (all `/*/py`) + `github-actions` updates.
