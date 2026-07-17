.PHONY: install install-dev lint lint-fix type test test-cov test-cov-ci license-check

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

lint:
	ruff check .
	ruff format . --check

lint-fix:
	ruff check . --fix
	ruff format .

type:
	pyright

test:
	pytest ./tests

test-cov:
	pytest ./tests --cov=./src --cov-report=xml

test-cov-ci:
	pytest ./tests --cov=./src --cov-report=xml

# License sweep (Loop 6 / D10): every resolved dependency must be permissively licensed.
# Allowed license strings live in ../../.licenses-allow.txt; manually-reviewed
# exceptions (the package list on the last line) live in ../../.licenses-exceptions.txt.
license-check:
	pip install -q pip-licenses
	pip-licenses --from=mixed --with-system \
	  --allow-only="$$(cat ../../.licenses-allow.txt)" \
	  --ignore-packages $$(tail -1 ../../.licenses-exceptions.txt) $$(pip list --format=freeze 2>/dev/null | grep -iE '^(nvidia-|cuda-)' | cut -d= -f1 | tr '\n' ' ')
