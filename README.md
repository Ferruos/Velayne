# Velayne Project

## Запуск

1. Установи зависимости:
   ```
   pip install -r requirements.txt
   ```

2. Укажи токен и свой Telegram ID в `.env`:
   ```
   TG_TOKEN=твой_токен
   ADMIN_ID=123456789
   ```

3. Добавь API-ключи через:
   ```
   python scripts/add_api_key.py
   ```

4. Запусти всё двойным кликом на `start_velayne.bat`.

## Управление

- Бот принимает команды, красиво оформленные.
- Админ-панель доступна только ADMIN_ID.
- Обучение моделей запускается из панели.
- Режим sandbox/live меняется кнопкой.
- Все ключи и данные в SQLite (velayne.db).