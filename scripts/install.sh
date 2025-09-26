#!/bin/bash
# Запускать из любого места; venv и cwd = корень репо

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Velayne: установка в $ROOT ==="

if [ ! -d ".venv" ]; then
  echo "=== Создание виртуального окружения (.venv) ==="
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "=== Обновление pip ==="
python -m pip install --upgrade pip

if [ ! -f "requirements.txt" ]; then
  echo "aiogram>=3.6
pydantic>=2.7
pydantic-settings>=2.3
python-dotenv>=1.0
loguru>=0.7
SQLAlchemy[asyncio]>=2.0
aiosqlite>=0.19
APScheduler>=3.10
ccxt>=4.3
feedparser>=6.0
cryptography>=42.0
onnx>=1.18
onnxruntime>=1.18
scikit-learn>=1.4
skl2onnx>=1.17
pandas>=2.2
pyarrow>=16.0
tenacity>=8.2
colorama>=0.4" > requirements.txt
fi

echo "=== Установка зависимостей ==="
python -m pip install -r requirements.txt

echo "=== Префлайт-проверка зависимостей ==="
python -m velayne.scripts.preflight --verbose
if [ $? -ne 0 ]; then
  echo "Префлайт провалился. Проверьте сообщения выше и повторите запуск."
  exit 1
fi

echo "=== Инициализация проекта ==="
python -m velayne.scripts.init

echo "=== Создание systemd-юнита ==="
cat <<EOF > velayne.service
[Unit]
Description=Velayne Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$ROOT
ExecStart=$ROOT/.venv/bin/python -m velayne.run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "=== Инструкции ==="
echo "sudo cp velayne.service /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl enable velayne.service"
echo "sudo systemctl start velayne.service"
echo "sudo systemctl status velayne.service"