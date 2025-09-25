@echo off
REM Запуск Redis (если есть локально)
start "" redis-server

REM Запуск master (публикация blend)
python master/main.py

REM Запуск Telegram-бота (в отдельном окне)
start "" python bot/bot.py

REM Запуск тестового воркера (демо)
start "" python workers/worker.py

pause