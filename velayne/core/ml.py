import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

DATA_PATH = Path("data/golden/ohlcv.parquet")

def load_golden_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    if path.exists():
        df = pd.read_parquet(path)
        df = df.sort_values("timestamp")
        return df
    # ... синтез
    n = 2000
    base = 10000
    ts = pd.date_range(datetime(2022,1,1), periods=n, freq="1min")
    close = base * (1 + 0.001 * pd.Series(range(n)).cumsum().apply(lambda x: (x % 10) / 100))
    df = pd.DataFrame({
        "timestamp": ts,
        "open": close,
        "high": close * 1.001,
        "low": close * 0.999,
        "close": close,
        "volume": 1
    })
    path.parent.mkdir(exist_ok=True, parents=True)
    df.to_parquet(path)
    return df

def simulate_strategy_on_data(df: pd.DataFrame) -> dict:
    # Dummy: PnL — рост цены, trades=N/50, sharpe=2.0
    pnl = df["close"].iloc[-1] - df["close"].iloc[0]
    return dict(net_pnl=pnl, trades=len(df)//50, sharpe=2.0)

def train_meta_model(df: pd.DataFrame) -> dict:
    # Dummy обучение
    X = df["close"].diff().fillna(0).values.reshape(-1,1)
    y = (df["close"].diff().fillna(0) > 0).astype(int)
    model = LogisticRegression().fit(X, y)
    acc = float(model.score(X, y))
    # Экспорт в ONNX
    onnx_path = Path("data/models/meta_model.onnx")
    onnx_path.parent.mkdir(exist_ok=True, parents=True)
    onnx = convert_sklearn(model, initial_types=[("input", FloatTensorType([None, 1]))])
    with open(onnx_path, "wb") as f:
        f.write(onnx.SerializeToString())
    return dict(acc=acc, onnx=str(onnx_path))