import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def get_logfile(name):
    return LOG_DIR / f"{name}.log"

def setup_logging():
    loggers = {
        "": get_logfile("velayne"),  # root
        "bot": get_logfile("bot"),
        "engine": get_logfile("engine"),
        "scheduler": get_logfile("scheduler"),
    }
    max_bytes = 10 * 1024 * 1024  # 10MB
    backup_count = 3

    for logger_name, file_path in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        # Also rotate daily by time
        timed_handler = TimedRotatingFileHandler(file_path, when="D", interval=1, backupCount=backup_count, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        timed_handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.addHandler(timed_handler)
        logger.setLevel(logging.INFO)

try:
    setup_logging()
    logger = logging.getLogger("velayne")
except Exception:
    logger = logging.getLogger()