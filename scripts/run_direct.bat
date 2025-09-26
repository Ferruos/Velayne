@echo on
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv ".venv" || python -m venv ".venv"
)
".venv\Scripts\python.exe" -X faulthandler -X utf8 -m velayne.run_standalone
pause