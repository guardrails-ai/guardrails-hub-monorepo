#!/usr/bin/env bash
# Regenerate the per-package dependency locks (py/requirements.lock) with uv.
#
# Most packages get a universal lock (valid across platforms and Python 3.10-3.13).
# A package whose universal resolution is unsatisfiable (e.g. TensorFlow, whose
# wheel matrix doesn't cover every platform/Python) falls back to a CI-targeted
# lock (linux, py3.13). A package that depends on a sibling not yet on PyPI is
# skipped with a warning; its lock will generate once that sibling is published.
set -uo pipefail
command -v uv >/dev/null 2>&1 || { echo "uv is required (pip install uv / pipx install uv)"; exit 1; }
cd "$(dirname "$0")/.."
universal=0; fallback=0; skipped=""
for d in */py; do
  [ -f "$d/pyproject.toml" ] || continue
  name=$(dirname "$d")
  # Pin to the minimum supported Python (3.10) so the lock installs across the
  # whole 3.10-3.13 matrix (newer interpreters accept these older pins).
  if uv pip compile --universal --python-version 3.10 --no-header --quiet "$d/pyproject.toml" -o "$d/requirements.lock" 2>/dev/null; then
    universal=$((universal+1))
  elif uv pip compile --python-platform x86_64-unknown-linux-gnu --python-version 3.10 \
        --no-header --quiet "$d/pyproject.toml" -o "$d/requirements.lock" 2>/dev/null; then
    fallback=$((fallback+1)); echo "  [linux/py3.10 fallback] $name"
  else
    rm -f "$d/requirements.lock"; skipped="$skipped $name"
    echo "  [SKIP unresolvable — e.g. depends on an unpublished sibling] $name"
  fi
done
echo "locked: ${universal} universal, ${fallback} CI-targeted; skipped:${skipped:- none}"
