# --- safe import guard: ensure repo root on sys.path ---
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
# -------------------------------------------------------

import os
import platform
import subprocess
import asyncio
import logging
import time
import shutil
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
print("=== Velayne Unified Launcher ===")
print(f"[LAUNCH] repo_root: {ROOT.resolve()}")
print(f"[LAUNCH] Python: {sys.version.split()[0]}  OS: {platform.system()} {platform.release()}")

env_path = ROOT / ".env"
log_path = ROOT / "logs" / "velayne.log"

if not env_path.exists():
    print(f"[LAUNCH] .env not found at {env_path}")
    template = (
        "TG_TOKEN=\n"
        "ADMIN_ID=\n"
        "SERVICE_MODE=sandbox\n"
        "EXCHANGE_TESTNET=true\n"
        "# Fill TG_TOKEN=bot_token, ADMIN_ID=your_id, EXCHANGE_TESTNET=true/false, SERVICE_MODE=sandbox/live\n"
    )
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"[LAUNCH] .env template created at {env_path}")
    print("Please edit .env and add your TG_TOKEN and ADMIN_ID, then restart.")
    sys.exit(5)
else:
    print(f"[LAUNCH] .env found: {env_path}")

try:
    from dotenv import load_dotenv
except ImportError:
    print("[LAUNCH] Installing python-dotenv...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path, override=False, verbose=False)

def mask(token):
    if not token:
        return "(not set)"
    return token[:3] + "***"

TG_TOKEN = os.environ.get("TG_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
SERVICE_MODE = os.environ.get("SERVICE_MODE", "sandbox")
EXCHANGE_TESTNET = os.environ.get("EXCHANGE_TESTNET", "true").lower() in ("true", "1", "yes")

print(f"[LAUNCH] TG_TOKEN: {mask(TG_TOKEN)} | ADMIN_ID: {ADMIN_ID or '(not set)'} | SERVICE_MODE: {SERVICE_MODE} | EXCHANGE_TESTNET: {EXCHANGE_TESTNET}")
print(f"[LAUNCH] logs path: {log_path.resolve()}")

# Try import velayne (main package)
try:
    import velayne
    print(f"[LAUNCH] import velayne: OK ({velayne.__file__})")
except Exception as e:
    print("[FATAL] Cannot import velayne package!")
    print("Tip: Run with -m velayne.launcher or check PYTHONPATH")
    print(e)
    sys.exit(4)

# ---- CHECK DEPENDENCIES ----
REQUIRED = [
    ("aiogram", "aiogram"),
    ("sqlalchemy", "sqlalchemy"),
    ("pandas", "pandas"),
    ("ccxt", "ccxt"),
    ("dotenv", "python-dotenv"),
]
missing = []
for mod, pkg in REQUIRED:
    try:
        __import__(mod)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f"[LAUNCH] Installing missing packages: {', '.join(missing)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    print("[LAUNCH] Packages installed. Please restart launcher.")
    sys.exit(3)

os.makedirs(ROOT / "logs", exist_ok=True)
os.makedirs(ROOT / "data", exist_ok=True)
golden_path = ROOT / "data" / "golden.parquet"
if not golden_path.exists():
    import pandas as pd
    df = pd.DataFrame([
        {"symbol": "BTC/USDT", "price": 10000, "dt": "2023-01-01T00:00:00Z"},
        {"symbol": "BTC/USDT", "price": 12000, "dt": "2023-01-02T00:00:00Z"},
        {"symbol": "BTC/USDT", "price": 11000, "dt": "2023-01-03T00:00:00Z"},
    ])
    df.to_parquet(golden_path)
    print("[LAUNCH] Golden dataset created.")

try:
    from velayne.infra.db import init_db_and_bootstrap
    asyncio.run(init_db_and_bootstrap())
except Exception as e:
    print(f"[LAUNCH][FATAL] DB init failed: {e}")
    sys.exit(4)

# ---- SELFTEST ----
print("[LAUNCH] Running quick selftest...")
code = subprocess.call([sys.executable, "scripts/selftest.py", "--quick"])
if code != 0:
    print("[LAUNCH][FATAL] Selftest failed! Check your config and logs.")
    sys.exit(4)
print("[LAUNCH] Selftest: PASS")

# ---- LOGGING ----
class TeeLogger:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            try:
                s.write(data)
                s.flush()
            except Exception:
                pass
    def flush(self): pass
sys.stdout = TeeLogger(sys.stdout, open(log_path, "a", encoding="utf-8"))
sys.stderr = TeeLogger(sys.stderr, open(log_path, "a", encoding="utf-8"))

print(f"[LAUNCH] --- Velayne Unified Start at {datetime.utcnow().isoformat()} ---")

async def run_scheduler():
    from velayne.infra.scheduler import start_scheduler
    await start_scheduler()

async def run_sandbox():
    from velayne.core.engine import start_sandbox_service
    await start_sandbox_service()

async def run_bot():
    from velayne.bot.main import start_bot
    await start_bot()

async def watchdog(factory, name, max_restarts=5):
    restarts = 0
    while restarts <= max_restarts:
        try:
            print(f"[WATCHDOG] Starting {name} (restart {restarts})")
            await factory()
            print(f"[WATCHDOG] {name} exited normally")
            break
        except Exception as e:
            restarts += 1
            print(f"[WATCHDOG] {name} crashed: {e} (restart {restarts}/{max_restarts})")
            time.sleep(3)
    if restarts > max_restarts:
        print(f"[WATCHDOG] {name} reached max restarts. Giving up.")

async def main():
    tasks = []
    print(f"[LAUNCH] Components: sandbox=ON, scheduler=ON, bot={'ON' if TG_TOKEN else 'OFF'}")
    tasks.append(asyncio.create_task(watchdog(run_scheduler, "scheduler")))
    tasks.append(asyncio.create_task(watchdog(run_sandbox, "sandbox")))
    if TG_TOKEN:
        tasks.append(asyncio.create_task(watchdog(run_bot, "bot")))
    await asyncio.sleep(1)
    print("[LAUNCH] RUNNING — Ctrl+C to stop")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[LAUNCH] Stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"[LAUNCH][FATAL] {e}")
        sys.exit(4)