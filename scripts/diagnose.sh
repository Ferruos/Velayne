#!/bin/bash

set -e

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment .venv..."
  python3 -m venv .venv
fi
source .venv/bin/activate

pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null

echo "---------------------------"
echo "Python version:"
python --version
echo "---------------------------"
echo "pip version:"
pip --version
echo "---------------------------"
echo "aiogram version:"
python -c "import aiogram; print(aiogram.__version__)"
echo "---------------------------"
echo "pydantic version:"
python -c "import pydantic; print(pydantic.__version__)"
echo "---------------------------"
echo "pydantic-settings version:"
python -c "import pydantic_settings; print(pydantic_settings.__version__)"
echo "---------------------------"
echo "SQLAlchemy version:"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
echo "---------------------------"
echo "onnx version:"
python -c "import onnx; print(onnx.__version__)"
echo "---------------------------"
echo "onnxruntime version:"
python -c "import onnxruntime; print(onnxruntime.__version__)"
echo "---------------------------"
echo "ccxt version:"
python -c "import ccxt; print(ccxt.__version__)" 2>/dev/null || true
echo "---------------------------"

python -m velayne.scripts.preflight --verbose
if [ $? -ne 0 ]; then
    echo
    echo "-----------------------------------------------"
    echo "[ERROR] Some dependencies or configs are missing!"
    echo "To fix ONNX:    pip install onnx==1.18 onnxruntime==1.18"
    echo "To fix Pydantic: pip install pydantic>=2.7 pydantic-settings>=2.3"
    echo "To fix aiogram:  pip install aiogram>=3.6"
    echo "For details, see README.md 'Диагностика'"
    echo "-----------------------------------------------"
    read -n 1 -s -r -p "Press any key to continue..."
    exit 1
fi

echo "Diagnose complete. All OK."
read -n 1 -s -r -p "Press any key to continue..."
exit 0