import os
import asyncio
from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

from velayne.infra.perf import DATAIO_BUFFERS

DATA_DIR = Path("data")
TRADES_DIR = DATA_DIR / "trades"
FEATURES_DIR = DATA_DIR / "features"
LABELS_DIR = DATA_DIR / "labels"

for d in [TRADES_DIR, FEATURES_DIR, LABELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def _date_str(dt):
    if isinstance(dt, str):
        dt = pd.Timestamp(dt)
    return dt.strftime("%Y%m%d")

async def _trades_flush(batch):
    if not batch:
        return
    date = _date_str(batch[0]['dt'])
    source = batch[0].get('source', 'sandbox')
    fpath = TRADES_DIR / f"trades_{date}_{source}.parquet"
    _parquet_append_batch(fpath, batch)

async def _features_flush(batch):
    if not batch:
        return
    date = _date_str(batch[0]['dt'])
    source = batch[0].get('source', 'sandbox')
    fpath = FEATURES_DIR / f"features_{date}_{source}.parquet"
    _parquet_append_batch(fpath, batch)

async def _labels_flush(batch):
    if not batch:
        return
    date = _date_str(batch[0]['dt'])
    source = batch[0].get('source', 'sandbox')
    fpath = LABELS_DIR / f"labels_{date}_{source}.parquet"
    _parquet_append_batch(fpath, batch)

DATAIO_BUFFERS.setup(_trades_flush, _features_flush, _labels_flush)

def append_trade(user_id, dt, symbol, side, qty, price, fee, pnl, strategy, latency_ms, regime, news_level, source='sandbox'):
    row = dict(
        user_id=user_id,
        dt=pd.Timestamp(dt),
        symbol=symbol,
        side=side,
        qty=qty,
        price=price,
        fee=fee,
        pnl=pnl,
        strategy=strategy,
        latency_ms=latency_ms,
        regime=regime,
        news_level=news_level,
        source=source,
    )
    asyncio.get_event_loop().create_task(DATAIO_BUFFERS.trades.append(row))

def append_features(user_id, dt, symbol, feat_dict, source='sandbox'):
    base = dict(user_id=user_id, dt=pd.Timestamp(dt), symbol=symbol, source=source)
    base.update(feat_dict)
    asyncio.get_event_loop().create_task(DATAIO_BUFFERS.features.append(base))

def append_label(user_id, dt, symbol, y, horizon_s, source='sandbox'):
    row = dict(
        user_id=user_id,
        dt=pd.Timestamp(dt),
        symbol=symbol,
        y=y,
        horizon_s=horizon_s,
        source=source,
    )
    asyncio.get_event_loop().create_task(DATAIO_BUFFERS.labels.append(row))

async def flush_all():
    await DATAIO_BUFFERS.shutdown()

def _parquet_append_batch(filepath, rows: list):
    if not rows:
        return
    df = pd.DataFrame(rows)
    table = pa.Table.from_pandas(df)
    if not filepath.exists():
        pq.write_table(table, filepath)
    else:
        old = pq.read_table(filepath)
        new_tbl = pa.concat_tables([old, table])
        pq.write_table(new_tbl, filepath)

def load_dataset(start_dt=None, end_dt=None, max_rows=None, sources: list = ['sandbox', 'live']) -> pd.DataFrame:
    def _get_files(d, prefix, sources):
        files = []
        for src in sources:
            files.extend(sorted([str(p) for p in d.glob(f"{prefix}_*_{src}.parquet")]))
        return files

    trades = []
    features = []
    labels = []
    for f in _get_files(TRADES_DIR, "trades", sources):
        trades.append(pd.read_parquet(f))
    for f in _get_files(FEATURES_DIR, "features", sources):
        features.append(pd.read_parquet(f))
    for f in _get_files(LABELS_DIR, "labels", sources):
        labels.append(pd.read_parquet(f))

    if not trades or not features or not labels:
        return pd.DataFrame()

    trades_df = pd.concat(trades, ignore_index=True)
    features_df = pd.concat(features, ignore_index=True)
    labels_df = pd.concat(labels, ignore_index=True)

    if start_dt:
        trades_df = trades_df[trades_df['dt'] >= pd.Timestamp(start_dt)]
        features_df = features_df[features_df['dt'] >= pd.Timestamp(start_dt)]
        labels_df = labels_df[labels_df['dt'] >= pd.Timestamp(start_dt)]
    if end_dt:
        trades_df = trades_df[trades_df['dt'] <= pd.Timestamp(end_dt)]
        features_df = features_df[features_df['dt'] <= pd.Timestamp(end_dt)]
        labels_df = labels_df[labels_df['dt'] <= pd.Timestamp(end_dt)]

    # Only keep rows for allowed sources
    trades_df = trades_df[trades_df['source'].isin(sources)]
    features_df = features_df[features_df['source'].isin(sources)]
    labels_df = labels_df[labels_df['source'].isin(sources)]

    df = trades_df.merge(features_df, on=["user_id", "dt", "symbol", "source"], suffixes=('', '_feat'))
    df = df.merge(labels_df, on=["user_id", "dt", "symbol", "source"])
    if max_rows:
        df = df.tail(max_rows)
    return df