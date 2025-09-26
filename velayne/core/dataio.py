import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from pathlib import Path
from velayne.infra.config import settings

DATA_DIR = Path(settings.DATA_DIR)
DATA_DIR.mkdir(exist_ok=True, parents=True)

def fetch_ohlcv(symbol, timeframe, since_ts):
    """
    Докачка OHLCV с помощью ccxt.
    symbol: строка, например 'BTC/USDT'
    timeframe: строка, например '1m', '5m'
    since_ts: unix timestamp (сек)
    Возвращает DataFrame с колонками: timestamp, open, high, low, close, volume
    """
    import ccxt
    exchange = ccxt.binance({
        "apiKey": getattr(settings, "BINANCE_API_KEY", ""),
        "secret": getattr(settings, "BINANCE_SECRET", ""),
        "enableRateLimit": True,
        "options": {
            "defaultType": "spot"
        }
    })
    if getattr(settings, "EXCHANGE_TESTNET", True):
        exchange.set_sandbox_mode(True)
    # Докачиваем максимум 1000 баров за раз
    bars = []
    limit = 1000
    now_ts = int(datetime.now(timezone.utc).timestamp()) * 1000
    last_ts = int(since_ts) * 1000 if since_ts else None
    while True:
        batch = exchange.fetch_ohlcv(symbol, timeframe, since=last_ts, limit=limit)
        if not batch:
            break
        bars.extend(batch)
        last_ts = bars[-1][0] + 1
        if len(batch) < limit or last_ts > now_ts:
            break
    # Преобразуем в DataFrame
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    return df

def save_parquet_incremental(path, df):
    """
    Сохраняет df в Parquet, добавляя новые строки и без дубликатов по timestamp.
    """
    path = Path(path)
    if path.exists():
        df0 = pd.read_parquet(path)
        df = pd.concat([df0, df], axis=0)
        df = df.drop_duplicates(subset="timestamp").sort_values("timestamp")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)

__all__ = [
    "fetch_ohlcv",
    "save_parquet_incremental"
]