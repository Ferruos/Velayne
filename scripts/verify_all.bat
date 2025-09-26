@echo off
setlocal

call .venv\Scripts\activate

echo === PRE-FLIGHT ===
python -m velayne.scripts.preflight --verbose || goto :fail

echo === RUFF ===
ruff check . || goto :fail

echo === BLACK ===
black --check . || goto :fail

echo === MYPY ===
mypy velayne || goto :fail

echo === BANDIT ===
bandit -q -r velayne -x tests || goto :fail

echo === PYTEST ===
pytest -q || goto :fail

echo === SELFTEST ===
python -m velayne.run --selftest || goto :fail

echo === PACKAGE (dry-run) ===
call scripts/package.bat dry-run || goto :fail

echo.
echo FINAL CHECK PASSED
exit /b 0

:fail
echo.
echo FINAL CHECK FAILED!
exit /b 1