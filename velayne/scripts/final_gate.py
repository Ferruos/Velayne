import sys
import os
import importlib
import traceback
import subprocess
import json
from pathlib import Path

def printc(txt, color="green"):
    c = {"red": "\033[91m", "green": "\033[92m", "reset": "\033[0m"}
    print(f"{c.get(color,'')}{txt}{c['reset']}")

def check_imports():
    required = [
        "aiogram", "pydantic", "pydantic_settings", "onnx", "onnxruntime", "skl2onnx", "scikit_learn",
        "pandas", "pyarrow", "sqlalchemy", "aiosqlite", "ccxt", "feedparser", "APScheduler", "tenacity",
        "cryptography", "loguru"
    ]
    errors = []
    for pkg in required:
        try:
            importlib.import_module(pkg.replace("_", "-") if pkg=="scikit_learn" else pkg)
        except Exception:
            errors.append(pkg)
    return errors

def check_ui():
    try:
        from velayne.bot import ui
        assert hasattr(ui, "mode_switch_message")
        return True
    except Exception:
        return False

def check_env_schema():
    from velayne.infra.config import Settings
    s = Settings()
    assert s.ADMIN_ID and s.ENCRYPTION_KEY is not None
    return True

def check_signal_model():
    path = Path("data/models/signal.onnx")
    if path.exists():
        return True
    try:
        from velayne.core.ml import train_from_logs
        train_from_logs()
        return path.exists()
    except Exception:
        return False

def check_db():
    try:
        from velayne.infra.db import Base, engine
        import asyncio
        async def create():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        asyncio.run(create())
        return True
    except Exception:
        return False

def mini_sandbox():
    import asyncio
    from velayne.core.engine import run_sandbox_loop, stop_sandbox_service
    async def tick():
        task = asyncio.create_task(run_sandbox_loop(0))
        await asyncio.sleep(2)
        await stop_sandbox_service()
    asyncio.run(tick())
    return True

def news_cache():
    try:
        from velayne.core.news import fetch_news
        items = fetch_news()
        return bool(items)
    except Exception:
        return False

def main():
    result = {"ok": True, "errors": []}
    try:
        print("== FINAL GATE ==")
        missing = check_imports()
        if missing:
            printc(f"Missing packages: {missing}", "red")
            result["ok"] = False
            result["errors"].append({"stage": "imports", "details": missing})
        if not check_ui():
            printc("UI: mode_switch_message not found", "red")
            result["ok"] = False
            result["errors"].append({"stage": "ui"})
        if not check_env_schema():
            printc("Env config schema failed", "red")
            result["ok"] = False
            result["errors"].append({"stage": "env"})
        if not check_signal_model():
            printc("Signal model not found and could not be generated", "red")
            result["ok"] = False
            result["errors"].append({"stage": "ml"})
        if not check_db():
            printc("DB migration/init failed", "red")
            result["ok"] = False
            result["errors"].append({"stage": "db"})
        if not mini_sandbox():
            printc("Mini sandbox tick failed", "red")
            result["ok"] = False
            result["errors"].append({"stage": "sandbox"})
        if not news_cache():
            printc("News cache fetch failed", "red")
            result["ok"] = False
            result["errors"].append({"stage": "news"})
    except Exception as e:
        printc("Exception in final gate: " + str(e), "red")
        traceback.print_exc()
        result["ok"] = False
        result["errors"].append({"stage": "exception", "details": str(e)})

    Path("logs").mkdir(exist_ok=True)
    with open("logs/final_gate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if result["ok"]:
        printc("FINAL GATE PASSED", "green")
        sys.exit(0)
    else:
        printc("FINAL GATE FAILED", "red")
        sys.exit(1)

if __name__ == "__main__":
    main()