import sys
import traceback
from pathlib import Path

def main():
    try:
        from velayne.infra.paths import data_dir, logs_dir
        data_path = data_dir()
        logs_path = logs_dir()
        print(f"[INFO] Data dir: {data_path}")
        print(f"[INFO] Logs dir: {logs_path}")
    except Exception as e:
        print("[FATAL] Не удалось создать папки logs/ или data/:", str(e))
        sys.exit(1)

    try:
        from velayne.infra.db import init_db_and_bootstrap, get_global_mode
        import asyncio
        asyncio.run(init_db_and_bootstrap())
        mode = asyncio.run(get_global_mode())
        print(f"[INFO] DB инициализирована, глобальный режим: {mode}")
    except Exception as e:
        print("[FATAL] Не удалось проинициализировать БД или получить глобальный режим:", str(e))
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()