import os
import json
import time
from pathlib import Path
from velayne.infra.logger import logger, setup_logging

def health_snapshot():
    snapshot = {
        "timestamp": int(time.time()),
        "db": False,
        "scheduler": False,
        "bot": False,
        "sandbox": False,
        "ml_model_presence": False,
        "news_cache_presence": False,
        "details": {},
    }
    try:
        from velayne.infra.db import engine
        snapshot["db"] = True
    except Exception as e:
        logger.error(f"DB healthcheck failed: {e}")
        snapshot["details"]["db"] = str(e)
    try:
        log_dir = Path("logs")
        data_dir = Path("data")
        log_dir.mkdir(exist_ok=True)
        data_dir.mkdir(exist_ok=True)
        snapshot["scheduler"] = True
    except Exception as e:
        logger.error(f"Scheduler healthcheck failed: {e}")
        snapshot["details"]["scheduler"] = str(e)
    try:
        from velayne.bot.ui import mode_switch_message
        snapshot["bot"] = True
    except Exception as e:
        logger.error(f"Bot healthcheck failed: {e}")
        snapshot["details"]["bot"] = str(e)
    try:
        from velayne.core.engine import run_sandbox_loop
        snapshot["sandbox"] = True
    except Exception as e:
        logger.error(f"Sandbox healthcheck failed: {e}")
        snapshot["details"]["sandbox"] = str(e)
    try:
        # ML model presence
        model_path = Path("data/models/signal.onnx")
        if model_path.exists():
            snapshot["ml_model_presence"] = True
        else:
            snapshot["details"]["ml_model_presence"] = "ML model missing"
    except Exception as e:
        snapshot["details"]["ml_model_presence"] = str(e)
    try:
        news_path = Path("data/news_cache.json")
        if news_path.exists():
            snapshot["news_cache_presence"] = True
        else:
            snapshot["details"]["news_cache_presence"] = "News cache missing"
    except Exception as e:
        snapshot["details"]["news_cache_presence"] = str(e)
    return snapshot

def self_heal():
    setup_logging()
    ok = True
    details = []
    # Try to create folders
    try:
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        Path("data/models").mkdir(exist_ok=True)
        details.append("Dirs OK")
    except Exception as e:
        logger.error(f"Cannot create dirs: {e}")
        details.append(f"Cannot create dirs: {e}")
        ok = False
    # Try to create ML model
    try:
        from velayne.core.ml import model as ml_model
        if not Path("data/models/signal.onnx").exists():
            ml_model._create_and_save_model()
            details.append("ML model created")
        else:
            details.append("ML model present")
    except Exception as e:
        logger.error(f"Cannot create ML model: {e}")
        details.append(f"Cannot create ML model: {e}")
        ok = False
    # Try to create news cache
    try:
        news_cache = Path("data/news_cache.json")
        if not news_cache.exists():
            with open(news_cache, "w", encoding="utf-8") as f:
                json.dump([], f)
            details.append("News cache created")
        else:
            details.append("News cache present")
    except Exception as e:
        logger.error(f"Cannot create news cache: {e}")
        details.append(f"Cannot create news cache: {e}")
        ok = False
    return {"ok": ok, "details": "; ".join(details)}