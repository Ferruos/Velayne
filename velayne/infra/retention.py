import os
from pathlib import Path
from datetime import datetime, timedelta
import json

from dotenv import load_dotenv
load_dotenv()

LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", 14))
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", 30))
NEWS_CACHE_RETENTION_DAYS = int(os.getenv("NEWS_CACHE_RETENTION_DAYS", 14))
MODELS_KEEP_LAST = int(os.getenv("MODELS_KEEP_LAST", 5))
DISK_SOFT_LIMIT_GB = float(os.getenv("DISK_SOFT_LIMIT_GB", 5))

BASE = Path("data")
LOGS = Path("logs")
TRADES = BASE / "trades"
FEATURES = BASE / "features"
LABELS = BASE / "labels"
MODELS = BASE / "models"
NEWS_CACHE = BASE / "news_cache.json"
NEWS_CACHE_DIR = BASE / "news_cache"

def _remove_files(files):
    total = 0
    for f in files:
        try:
            sz = f.stat().st_size
            f.unlink()
            total += sz
        except Exception:
            pass
    return total

def cleanup_logs():
    now = datetime.utcnow()
    cutoff = now - timedelta(days=LOG_RETENTION_DAYS)
    removed = []
    for f in LOGS.glob("*.log*"):
        mtime = datetime.utcfromtimestamp(f.stat().st_mtime)
        if mtime < cutoff:
            try:
                sz = f.stat().st_size
                f.unlink()
                removed.append((f.name, sz))
            except Exception:
                pass
    return {"logs_removed": len(removed), "space_freed": sum(sz for _, sz in removed)}

def cleanup_datasets():
    now = datetime.utcnow()
    cutoff = now - timedelta(days=DATA_RETENTION_DAYS)
    removed = []
    compacted = []
    data_dirs = [TRADES, FEATURES, LABELS]
    for d in data_dirs:
        for f in d.glob("*.parquet"):
            date_part = f.name.split("_")[-1].replace(".parquet", "")
            try:
                fdate = datetime.strptime(date_part, "%Y%m%d")
                if fdate < cutoff:
                    sz = f.stat().st_size
                    f.unlink()
                    removed.append((str(f), sz))
            except Exception:
                pass
    return {"datasets_removed": len(removed), "space_freed": sum(sz for _, sz in removed)}

def cleanup_news_cache():
    now = datetime.utcnow()
    cutoff = now - timedelta(days=NEWS_CACHE_RETENTION_DAYS)
    removed_files = 0
    removed_recs = 0
    # If directory with cache files (per day)
    if NEWS_CACHE_DIR.exists():
        for f in NEWS_CACHE_DIR.glob("*.json"):
            mtime = datetime.utcfromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                try:
                    f.unlink()
                    removed_files += 1
                except Exception:
                    pass
    # If one file with list of dicts (default)
    if NEWS_CACHE.exists():
        try:
            with open(NEWS_CACHE, "r", encoding="utf-8") as fp:
                items = json.load(fp)
            new_items = [rec for rec in items if "published" in rec and
                         (datetime.fromisoformat(rec["published"]) if rec.get("published") else now) >= cutoff]
            removed_recs = len(items) - len(new_items)
            if removed_recs:
                with open(NEWS_CACHE, "w", encoding="utf-8") as fp:
                    json.dump(new_items, fp)
        except Exception:
            pass
    return {"news_cache_files_removed": removed_files, "news_cache_records_removed": removed_recs}

def cleanup_models():
    # Keep only last MODELS_KEEP_LAST (by modified date)
    model_files = sorted(MODELS.glob("signal*.onnx"), key=lambda f: f.stat().st_mtime, reverse=True)
    meta_files = sorted(MODELS.glob("meta*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    to_remove = model_files[MODELS_KEEP_LAST:] + meta_files[MODELS_KEEP_LAST:]
    removed = []
    for f in to_remove:
        try:
            sz = f.stat().st_size
            f.unlink()
            removed.append((str(f), sz))
        except Exception:
            pass
    return {"models_removed": len(removed), "space_freed": sum(sz for _, sz in removed)}

def _dir_size_mb(path: Path):
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total / 1024 / 1024

def enforce_disk_soft_limit():
    dirs = [LOGS, TRADES, FEATURES, LABELS, MODELS]
    limit_bytes = DISK_SOFT_LIMIT_GB * 1024 * 1024 * 1024
    stats = {}
    total = sum(_dir_size_mb(d) for d in dirs)
    before = total
    if total * 1024 * 1024 > limit_bytes:
        stats["logs"] = cleanup_logs()
        stats["datasets"] = cleanup_datasets()
        stats["news_cache"] = cleanup_news_cache()
        stats["models"] = cleanup_models()
        after = sum(_dir_size_mb(d) for d in dirs)
        stats["freed_mb"] = before - after
    stats["total_mb_before"] = before
    stats["total_mb_after"] = sum(_dir_size_mb(d) for d in dirs)
    return stats

def retention_summary():
    stats = {}
    stats["logs"] = cleanup_logs()
    stats["datasets"] = cleanup_datasets()
    stats["news_cache"] = cleanup_news_cache()
    stats["models"] = cleanup_models()
    stats["disk_limit"] = enforce_disk_soft_limit()
    return stats

def retention_policy_summary():
    return {
        "LOG_RETENTION_DAYS": LOG_RETENTION_DAYS,
        "DATA_RETENTION_DAYS": DATA_RETENTION_DAYS,
        "NEWS_CACHE_RETENTION_DAYS": NEWS_CACHE_RETENTION_DAYS,
        "MODELS_KEEP_LAST": MODELS_KEEP_LAST,
        "DISK_SOFT_LIMIT_GB": DISK_SOFT_LIMIT_GB,
    }