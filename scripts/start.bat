@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0.."

REM -- Python check --
py -3 -V >nul 2>&1
if not "%ERRORLEVEL%"=="0" (
  python -V >nul 2>&1
  if not "%ERRORLEVEL%"=="0" (
    echo [FATAL] Python не найден. Установите Python 3.x и добавьте в PATH.
    pause
    exit /b 2
  )
)

REM -- Venv check --
if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Создание виртуального окружения...
  py -3 -m venv ".venv"
)
if not exist ".venv\Scripts\python.exe" (
  echo [FATAL] venv не удалось создать!
  pause
  exit /b 2
)

REM -- Pip install --
echo [INFO] Установка/обновление зависимостей...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if not "%ERRORLEVEL%"=="0" (
  echo [FATAL] pip install не выполнен. Проверьте requirements.txt и интернет.
  pause
  exit /b 3
)

REM -- Editable install --
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -e .
if not "%ERRORLEVEL%"=="0" (
  echo [WARN] pip install -e . не выполнен. Продолжаем.
)

REM -- Явный вывод конфигурации --
if exist .env (
  echo [INFO] .env найден:
  type .env
) else (
  echo [WARN] .env отсутствует!
)

REM -- Запуск unified Python launcher как модуля --
".venv\Scripts\python.exe" -X faulthandler -X utf8 -m velayne.run
set EXITCODE=%ERRORLEVEL%
if not "%EXITCODE%"=="0" (
  echo [FATAL] Завершение с кодом %EXITCODE%.
  pause
  exit /b %EXITCODE%
)

echo.
echo [INFO] RUNNING — Ctrl+C для остановки
pause
endlocal