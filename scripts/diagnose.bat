@echo off
setlocal

REM === Activate venv or create if not exists ===
if not exist ".venv\" (
    echo Creating virtual environment .venv...
    python -m venv .venv
)
call .venv\Scripts\activate

REM === Install requirements ===
pip install --upgrade pip >nul
pip install -r requirements.txt >nul

REM === Show versions ===
echo ---------------------------
echo Python version:
python --version
echo ---------------------------
echo pip version:
pip --version
echo ---------------------------
echo aiogram version:
python -c "import aiogram; print(aiogram.__version__)"
echo ---------------------------
echo pydantic version:
python -c "import pydantic; print(pydantic.__version__)"
echo ---------------------------
echo pydantic-settings version:
python -c "import pydantic_settings; print(pydantic_settings.__version__)"
echo ---------------------------
echo SQLAlchemy version:
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
echo ---------------------------
echo onnx version:
python -c "import onnx; print(onnx.__version__)"
echo ---------------------------
echo onnxruntime version:
python -c "import onnxruntime; print(onnxruntime.__version__)"
echo ---------------------------
echo ccxt version:
python -c "import ccxt; print(ccxt.__version__)" 2>NUL

REM === Run preflight ===
python -m velayne.scripts.preflight --verbose
if errorlevel 1 (
    echo.
    echo -----------------------------------------------
    echo [ERROR] Some dependencies or configs are missing!
    echo To fix ONNX:    pip install onnx==1.18 onnxruntime==1.18
    echo To fix Pydantic: pip install pydantic>=2.7 pydantic-settings>=2.3
    echo To fix aiogram:  pip install aiogram>=3.6
    echo For details, see README.md 'Диагностика'
    echo -----------------------------------------------
    pause
    exit /b 1
)

echo Diagnose complete. All OK.
pause
exit /b 0