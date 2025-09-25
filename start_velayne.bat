@echo off
cd /d %~dp0
python -c "from storage.db import init_db; init_db()"
start cmd /k python master\master.py
start cmd /k python bot\bot.py
start cmd /k uvicorn webapp.main:app --reload
start cmd /k python workers\worker.py
pause