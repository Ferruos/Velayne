# Velayne

---

## Запуск одним окном (Windows/Linux)

**Windows (двойной клик):**

1. Откройте проводник, перейдите в папку проекта.
2. Дважды кликните `scripts/start.bat`  
   - venv создается в корне (`.venv`), cwd автоматически ставится в корень проекта
   - Все зависимости и папки будут установлены
   - Префлайт проверит Python 3.11+, onnx, pydantic, requirements.txt, наличие модуля velayne
   - После запуска бот и sandbox будут работать в ЭТОМ ОКНЕ (ничего не закроется)
3. Если появилось красное сообщение — внимательно изучите подсказку (например, для onnx или pip)
4. Если `.env` не найден — скопируйте `.env.example` и заполните TG_TOKEN, ADMIN_ID, ENCRYPTION_KEY

**Linux:**

1. Выполните `bash scripts/install.sh`
   - venv в `.venv`, cwd = корень
   - requirements.txt обязательный (будет создан, если нет)
2. Для автозапуска используйте systemd-юнит:
   - `sudo cp velayne.service /etc/systemd/system/`
   - `sudo systemctl daemon-reload`
   - `sudo systemctl enable velayne.service`
   - `sudo systemctl start velayne.service`
   - `sudo systemctl status velayne.service`

**Все пути/импорты работают из КОРНЯ репозитория!**

---

## Частые ошибки и их решение

- **Python < 3.11** — обновите Python: https://www.python.org/downloads/
- **Модуль onnx/onnxruntime не найден**  
  `python -m pip install onnx==1.18 onnxruntime==1.18`
- **Ошибка "BaseSettings moved"**  
  `python -m pip install pydantic-settings pydantic>=2.7`
- **Нет requirements.txt**  
  Запустите start.bat — requirements.txt будет создан автоматически в корне
- **Нет TG_TOKEN/ADMIN_ID**  
  Скопируйте .env.example → .env и заполните переменные

---

## Финальная проверка

- `scripts/final_gate.bat` (Windows) или `scripts/final_gate.sh` (Linux)
- Либо: `python -m velayne.scripts.final_gate`
- Финальный отчет — в logs/final_gate.json
- Для диагностики: `python -m velayne.run --selftest` (Быстрый прогон всех сервисов)

---

## Обновление pip и установка зависимостей вручную

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install onnx==1.18 onnxruntime==1.18
python -m pip install pydantic-settings pydantic>=2.7
```

---

## Дополнительно

- Все команды запускаются из корня (`cwd` ставится автоматически)
- Если start.bat не активирует venv или не видит зависимости — проверьте права и версию Python
- Для быстрой проверки кода:  
  `ruff check .`  
  `black --check .`  
  `mypy velayne`  
  `bandit -q -r velayne -x tests`

---