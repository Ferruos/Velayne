@echo off
REM Запуск Velayne в одном окне, venv и cwd = корень репозитория
chcp 65001 >nul
set PYTHONUTF8=1

REM Определить корень проекта (папка выше scripts)
set "ROOT=%~dp0.."
pushd "%ROOT%"

echo === Velayne: запуск в %CD% ===

REM Проверка наличия .venv
if not exist ".\.venv\" (
    echo === Создание виртуального окружения (.venv) ===
    python -m venv .venv
    if errorlevel 1 (
        echo [FATAL] Не удалось создать venv. Проверьте установку Python 3.11+.
        pause
        popd
        exit /b 1
    )
)

call .venv\Scripts\activate

REM Обновить pip
echo === Обновление pip ===
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [FATAL] Не удалось обновить pip. Попробуйте вручную: python -m pip install --upgrade pip
    pause
    popd
    exit /b 1
)

REM Проверка requirements.txt
if not exist ".\requirements.txt" (
    echo === Создание минимального requirements.txt ===
    echo aiogram>=3.6> requirements.txt
    echo pydantic>=2.7>> requirements.txt
    echo pydantic-settings>=2.3>> requirements.txt
    echo python-dotenv>=1.0>> requirements.txt
    echo loguru>=0.7>> requirements.txt
    echo SQLAlchemy[asyncio]>=2.0>> requirements.txt
    echo aiosqlite>=0.19>> requirements.txt
    echo APScheduler>=3.10>> requirements.txt
    echo ccxt>=4.3>> requirements.txt
    echo feedparser>=6.0>> requirements.txt
    echo cryptography>=42.0>> requirements.txt
    echo onnx>=1.18>> requirements.txt
    echo onnxruntime>=1.18>> requirements.txt
    echo scikit-learn>=1.4>> requirements.txt
    echo skl2onnx>=1.17>> requirements.txt
    echo pandas>=2.2>> requirements.txt
    echo pyarrow>=16.0>> requirements.txt
    echo tenacity>=8.2>> requirements.txt
    echo colorama>=0.4>> requirements.txt
)

REM Установка зависимостей
echo === Установка зависимостей ===
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [FATAL] Не удалось установить зависимости. Проверьте requirements.txt или попробуйте вручную: python -m pip install -r requirements.txt
    pause
    popd
    exit /b 1
)

REM Префлайт
echo === Префлайт-проверка зависимостей ===
python -X utf8 -m velayne.scripts.preflight --verbose
if errorlevel 1 (
    echo [\033[91mFATAL\033[0m] Префлайт-проверка провалена. Проверьте ошибки выше и повторите запуск.
    pause
    popd
    exit /b 1
)

REM Инициализация проекта
echo === Инициализация проекта ===
python -X utf8 -m velayne.scripts.init
if errorlevel 1 (
    echo [FATAL] Инициализация провалена.
    pause
    popd
    exit /b 1
)

REM Запуск сервиса
echo === Запуск Velayne (бот, sandbox, планировщик) ===
python -X utf8 -m velayne.run
if errorlevel 1 (
    echo [FATAL] Произошла ошибка. Проверьте логи или обратитесь в поддержку.
    pause
    popd
    exit /b 1
)

popd
exit /b 0