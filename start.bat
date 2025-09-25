@echo off
REM Запускает оптимизацию (main.py) и затем воркер (worker.py).
REM Обязательно активируйте ваше venv или пропишите путь к python.exe.
call venv\Scripts\activate.bat

python master\main.py

REM После публикации blend запускаем воркер, который будет торговать на песочнице.
start "worker" python workers\worker.py

echo Нажмите любую клавишу, чтобы завершить...
pause > nul
