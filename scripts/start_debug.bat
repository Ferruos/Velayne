@echo on
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0.."

echo [DEBUG] Python version:
py -3 -V 2>&1
if not "%ERRORLEVEL%"=="0" (
  python -V 2>&1
  if not "%ERRORLEVEL%"=="0" (
    echo [FATAL] Python not found!
    pause
    exit /b 2
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creating virtual environment...
  py -3 -m venv ".venv"
)
if not exist ".venv\Scripts\python.exe" (
  echo [FATAL] venv creation failed!
  pause
  exit /b 2
)

echo [DEBUG] Checking pip and installed packages:
".venv\Scripts\python.exe" -m pip list

echo [DEBUG] .env contents:
if exist ".env" (
  type ".env"
) else (
  echo [WARN] .env not found!
)

echo [DEBUG] Installing/upgrading dependencies...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt

echo [DEBUG] pip install -e . (editable mode)...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -e .

echo [DEBUG] Printing last 20 lines of logs\velayne.log:
if exist logs\velayne.log (
  more +0 logs\velayne.log | tail -n 20
)

echo [DEBUG] Launching main program as module...
".venv\Scripts\python.exe" -X faulthandler -X utf8 -m velayne.launcher
set EXITCODE=%ERRORLEVEL%
if not "%EXITCODE%"=="0" (
  echo [FATAL] Application exited with code %EXITCODE%.
  pause
  exit /b %EXITCODE%
)

echo.
echo [INFO] RUNNING — Ctrl+C to stop
pause
endlocal