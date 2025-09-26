import logging
import sys
from pathlib import Path
from datetime import datetime

from velayne.infra.config import settings

LOG_DIR = Path(settings.LOG_DIR)
LOG_DIR.mkdir(exist_ok=True, parents=True)
LOG_FILE = LOG_DIR / "velayne.log"

class RussianFormatter(logging.Formatter):
    def format(self, record):
        ts = datetime.fromtimestamp(record.created).strftime('%d.%m.%Y %H:%M:%S')
        prefix = f"[{ts}] [{record.levelname}] [{record.module}]"
        msg = super().format(record)
        return f"{prefix} {msg}"

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = RussianFormatter('%(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(ch)
    logger.addHandler(fh)
    return str(LOG_FILE)