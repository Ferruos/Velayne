import asyncio
from pathlib import Path
from velayne.infra.config import settings
from velayne.infra.db import init_db_and_migrate_state, get_users_count, get_global_mode

def ensure_dirs():
    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)

def main():
    ensure_dirs()
    print("Инициализация папок...")
    asyncio.run(init_db_and_migrate_state("data/state.json"))
    print("Миграция состояния завершена.")
    users_count = asyncio.run(get_users_count())
    mode = asyncio.run(get_global_mode())
    print(f"Пользователей в системе: {users_count}")
    print(f"Текущий режим: {mode}")

if __name__ == "__main__":
    main()