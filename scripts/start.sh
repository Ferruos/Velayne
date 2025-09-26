#!/bin/bash
set -e

cd "$(dirname "$0")/.."

if ! command -v python3 &>/dev/null; then
  echo "[FATAL] Python 3.x не найден!"
  exit 2
fi

if [ ! -f .venv/bin/python ]; then
  echo "[INFO] Создаю виртуальное окружение..."
  python3 -m venv .venv
fi

if [ ! -f .venv/bin/python ]; then
  echo "[FATAL] venv не удалось создать!"
  exit 2
fi

echo "[INFO] Установка зависимостей..."
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python -m pip install --disable-pip-version-check -e .

if [ -f .env ]; then
  echo "[INFO] .env найден:"
  cat .env
else
  echo "[WARN] .env отсутствует!"
fi

echo "[INFO] Запуск unified launcher..."
.venv/bin/python -X utf8 -m velayne.run
code=$?
if [ "$code" != "0" ]; then
  echo "[FATAL] Программа завершилась с кодом $code"
  exit $code
fi

echo
echo "[INFO] RUNNING — Ctrl+C для выхода"
read -n 1 -s -r -p "Нажмите любую клавишу для выхода..."
echo