@echo off
setlocal

REM === Проверка Python >= 3.11 ===
python --version > tmp_pyver.txt 2>&1
set /p PYV=<tmp_pyver.txt
del tmp_pyver.txt

for /f "tokens=2 delims= " %%A in ("%PYV%") do set VER=%%A
for /f "tokens=1,2 delims=." %%A in ("%VER%") do (
    set MAJOR=%%A
    set MINOR=%%B
)
if "%MAJOR%"=="" (
    echo [ERROR] Python не найден. Установите Python 3.11+ и добавьте в PATH.
    pause
    exit /b 1
)
if %MAJOR% LSS 3 (
    echo [ERROR] Требуется Python 3.11 или новее.
    pause
    exit /b 1
)
if %MAJOR%==3 if %MINOR% LSS 11 (
    echo [ERROR] Требуется Python 3.11 или новее.
    pause
    exit /b 1
)

REM === Создание/активация venv ===
if not exist ".venv\" (
    echo [INFO] Создаю виртуальное окружение .venv...
    python -m venv .venv
)
call .venv\Scripts\activate

REM === Установка зависимостей ===
echo [INFO] Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

REM === Инициализация данных ===
echo [INFO] Инициализация...
python -m velayne.scripts.init

REM === Запуск сервиса ===
echo [INFO] Запуск сервиса...
python -m velayne.run

pause