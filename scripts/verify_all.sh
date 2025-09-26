#!/bin/bash
set -e

source .venv/bin/activate

echo "=== PRE-FLIGHT ==="
python -m velayne.scripts.preflight --verbose

echo "=== RUFF ==="
ruff check .

echo "=== BLACK ==="
black --check .

echo "=== MYPY ==="
mypy velayne

echo "=== BANDIT ==="
bandit -q -r velayne -x tests

echo "=== PYTEST ==="
pytest -q

echo "=== SELFTEST ==="
python -m velayne.run --selftest

echo "=== PACKAGE (dry-run) ==="
bash scripts/package.sh dry-run

echo ""
echo "FINAL CHECK PASSED"