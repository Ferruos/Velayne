import os
from velayne.infra.paths import data_dir, logs_dir, project_root

def main():
    data_path = data_dir()
    logs_path = logs_dir()
    models_path = data_path / "models"
    models_path.mkdir(parents=True, exist_ok=True)
    env_path = project_root() / ".env"
    env_example_path = project_root() / ".env.example"
    if not env_path.exists():
        print("Внимание: .env не найден! Скопируйте .env.example -> .env и заполните TG_TOKEN, ADMIN_ID.")
        if not env_example_path.exists():
            with open(env_example_path, "w", encoding="utf-8") as f:
                f.write(
                    "TG_TOKEN=\nADMIN_ID=\nENCRYPTION_KEY=\nYOOKASSA_SHOP_ID=\nYOOKASSA_SECRET=\nDB_URL=sqlite+aiosqlite:///data/velayne.db\nLOG_DIR=logs\nDATA_DIR=data\nEXCHANGE_TESTNET=true\nORDER_QUEUE_MAX_PARALLEL=3\nORDER_QUEUE_MAX_PER_SEC=5\nLOG_RETENTION_DAYS=14\nDATA_RETENTION_DAYS=30\nNEWS_CACHE_RETENTION_DAYS=14\nMODELS_KEEP_LAST=5\nDISK_SOFT_LIMIT_GB=5\nDEFAULT_TZ=UTC\n"
                )
            print(".env.example создан.")
    print(f"Стартовая инициализация: data={data_path}, logs={logs_path}, models={models_path}")
    # Лог (кратко)
    with open(logs_path / "init.log", "a", encoding="utf-8") as f:
        f.write("Init complete\n")

if __name__ == "__main__":
    main()