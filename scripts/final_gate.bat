@echo off
setlocal

call .venv\Scripts\activate

python -m velayne.scripts.final_gate

if %ERRORLEVEL% EQU 0 (
    echo FINAL GATE PASSED
) else (
    echo FINAL GATE FAILED -- see logs/final_gate.json for details
)
exit /b %ERRORLEVEL%