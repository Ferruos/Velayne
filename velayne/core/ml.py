import os
import json
from pathlib import Path
import numpy as np
import pandas as pd

MODEL_PATH = Path("data/models/signal.onnx")
META_PATH = Path("data/models/meta.json")
STRATEGY_MIX_PATH = Path("data/models/strategy_mix.json")
MODEL_HISTORY_PATH = Path("data/models/model_history.json")
os.makedirs(MODEL_PATH.parent, exist_ok=True)

def extract_features(market: dict, portfolio: dict, news: dict) -> dict:
    symbol = list(market.keys())[0]
    m = market[symbol]
    import numpy as np
    closes = m.get("close", [100])
    returns = np.array([closes[i] - closes[i-1] for i in range(1, len(closes))]) if len(closes) > 1 else np.zeros(1)
    returns_std = np.std(returns)
    returns_mean = np.mean(returns)
    # Примитивная волатильность (можно заменить surrogate GARCH)
    vol_ema = pd.Series(np.abs(returns)).ewm(span=10).mean().iloc[-1] if len(returns) > 10 else float(returns_std)
    features = {
        "atr": float(m.get("atr", 1)),
        "rsi": float(m.get("rsi", 50)),
        "ema_gap": float(m.get("ema_short", 0) - m.get("ema_long", 0)),
        "returns": float(returns_mean),
        "returns_std": float(returns_std),
        "vol_ema": float(vol_ema),
        "spread": float(m.get("spread", 0.1)),
        "news_count": float(news.get("count", 0)),
        "news_level": {"NONE": 0, "CAUTION": 1, "RED": 2}.get(news.get("level", "NONE"), 0),
    }
    return features

def infer_proba(features: dict, blend_meta: dict = None) -> float:
    # Ансамбль: rule-based + ML + volatility-model
    ml_score = _infer_ml(features)
    rule_score = _rule_based_score(features)
    vol_score = _volatility_score(features)
    weights = [0.5, 0.3, 0.2]  # default blending
    if blend_meta and "blend_weights" in blend_meta:
        weights = blend_meta["blend_weights"]
    score = weights[0]*ml_score + weights[1]*rule_score + weights[2]*vol_score
    return min(max(score, 0), 1)

def _infer_ml(features: dict) -> float:
    import onnxruntime as ort
    import numpy as np
    if not Path(MODEL_PATH).exists():
        return 0.5
    sess = ort.InferenceSession(str(MODEL_PATH))
    feats = sorted(features.keys())
    input_arr = np.array([[features[k] for k in feats]], dtype=np.float32)
    input_name = sess.get_inputs()[0].name
    prob = sess.run(None, {input_name: input_arr})[1]
    score = float(prob[0][1]) if prob.shape[-1] > 1 else float(prob[0][0])
    return score

def _rule_based_score(features: dict) -> float:
    # Примитив: если ema_gap > 0 и rsi < 65 → 0.7, если rsi > 80 → 0.2
    ema_gap = features.get('ema_gap', 0)
    rsi = features.get('rsi', 50)
    if ema_gap > 0 and rsi < 65:
        return 0.7
    elif rsi > 80:
        return 0.2
    else:
        return 0.5

def _volatility_score(features: dict) -> float:
    # Если returns_std > threshold (высокая волатильность) — понижаем вероятность сигнала
    std = features.get("returns_std", 0.01)
    vol_ema = features.get("vol_ema", std)
    if vol_ema > 2.0:
        return 0.2
    elif vol_ema < 0.5:
        return 0.7
    else:
        return 0.5

def train_from_logs(start_dt=None, end_dt=None, sources=['sandbox', 'live'], weights={'sandbox': 0.5, 'live': 1.0}):
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import RobustScaler
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, roc_curve

    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType

    from velayne.core.dataio import load_dataset
    df = load_dataset(start_dt, end_dt, sources=sources)
    if df.empty or len(df) < 300:
        return None

    feats = ["atr", "rsi", "ema_gap", "returns", "returns_std", "vol_ema", "spread", "news_count", "news_level"]
    X = df[feats].replace([np.inf, -np.inf], np.nan).fillna(0)
    y = df["y"].astype(int)
    src = df["source"].values

    sample_weights = np.array([weights.get(s, 1.0) for s in src])
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    df_sorted = df.sort_values("dt")
    split_idx = int(len(df_sorted)*0.8)
    X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    w_train, w_test = sample_weights[:split_idx], sample_weights[split_idx:]
    s_train, s_test = src[:split_idx], src[split_idx:]

    clf = GradientBoostingClassifier(n_estimators=50)
    clf.fit(X_train, y_train, sample_weight=w_train)
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:,1]

    auc = roc_auc_score(y_test, y_proba)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    best_thresh = 0.5
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    youden = tpr - fpr
    idx = np.argmax(youden)
    if 0 <= idx < len(thresholds):
        best_thresh = thresholds[idx]

    meta = {
        "auc": float(auc),
        "accuracy": float(acc),
        "f1": float(f1),
        "best_thresh": float(best_thresh),
        "version": 1,
        "updated": pd.Timestamp.utcnow().isoformat(),
        "features": feats,
        "scaler": "RobustScaler",
        "model": "GradientBoostingClassifier",
        "sample_count": int(len(df)),
        "sources": {},
        "cv_curve": [],
        "fallback_mode": False,
        "model_weight": 1.0,
        "blend_weights": [0.5, 0.3, 0.2],
        "blending_history": [],
    }
    # Пер-источник метрики
    for src_name in set(s_test):
        mask = s_test == src_name
        if mask.sum():
            auci = roc_auc_score(y_test[mask], y_proba[mask])
            acci = accuracy_score(y_test[mask], y_pred[mask])
            f1i = f1_score(y_test[mask], y_pred[mask])
            meta["sources"][src_name] = {
                "auc": float(auci),
                "accuracy": float(acci),
                "f1": float(f1i),
                "count": int(mask.sum()),
            }

    # ONNX
    initial_type = [("float_input", FloatTensorType([None, len(feats)]))]
    onnx_model = convert_sklearn(clf, initial_types=initial_type)
    prev_models = []
    if Path(MODEL_HISTORY_PATH).exists():
        prev_models = json.load(open(MODEL_HISTORY_PATH, "r", encoding="utf-8"))
    meta["version"] = (prev_models[-1]["version"]+1) if prev_models else 1

    # walk-forward-validate
    curve = walk_forward_validation(df, feats, weights)
    meta["cv_curve"] = curve

    # --- Ансамбль: blending ---
    blend_weights, blending_history = blend_ensemble_last_days(df, feats)
    meta["blend_weights"] = blend_weights
    meta["blending_history"] = blending_history

    # Откат/снижение веса при плохих валидациях
    fallback, model_weight = validate_cv_curve(curve)
    meta["fallback_mode"] = fallback
    meta["model_weight"] = model_weight

    with open(MODEL_PATH, "wb") as f:
        f.write(onnx_model.SerializeToString())
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f)
    prev_models.append(meta)
    with open(MODEL_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(prev_models[-10:], f)

    return meta

def walk_forward_validation(df: pd.DataFrame, feats, weights=None, n_windows=5):
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import RobustScaler
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score
    import numpy as np

    curve = []
    if df.empty or len(df) < 300:
        return curve
    df = df.sort_values("dt")
    window = len(df) // (n_windows + 1)
    for i in range(n_windows):
        train_idx = slice(0, window * (i+1))
        val_idx = slice(window * (i+1), window * (i+2))
        df_train = df.iloc[train_idx]
        df_val = df.iloc[val_idx]
        if len(df_train) < 100 or len(df_val) < 100:
            continue
        X_train = df_train[feats].replace([np.inf, -np.inf], np.nan).fillna(0)
        X_val = df_val[feats].replace([np.inf, -np.inf], np.nan).fillna(0)
        y_train = df_train["y"].astype(int)
        y_val = df_val["y"].astype(int)
        sw_train = np.array([weights.get(s, 1.0) for s in df_train["source"]]) if weights else None
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        clf = GradientBoostingClassifier(n_estimators=50)
        clf.fit(X_train_scaled, y_train, sample_weight=sw_train)
        y_pred = clf.predict(X_val_scaled)
        y_proba = clf.predict_proba(X_val_scaled)[:,1]
        auc = roc_auc_score(y_val, y_proba)
        acc = accuracy_score(y_val, y_pred)
        f1 = f1_score(y_val, y_pred)
        curve.append({
            "window": i,
            "auc": float(auc),
            "accuracy": float(acc),
            "f1": float(f1),
            "count": int(len(y_val))
        })
    return curve

def validate_cv_curve(curve, drop_thresh=0.15):
    if not curve:
        return (True, 0.0)  # fallback
    f1s = [c["f1"] for c in curve]
    if not f1s:
        return (True, 0.0)
    maxf1 = max(f1s)
    minf1 = min(f1s)
    avgf1 = sum(f1s) / len(f1s)
    if minf1 < maxf1 * (1 - drop_thresh):
        model_weight = min(0.5, avgf1)
        return (False, model_weight)
    if avgf1 < 0.55:
        return (True, 0.0)
    return (False, 1.0)

def blend_ensemble_last_days(df, feats, window_days=7):
    # Подбор blending весов по последним X дней, минимизация ошибки (grid search)
    import numpy as np
    from sklearn.metrics import f1_score
    if "dt" not in df or "y" not in df:
        return [0.5, 0.3, 0.2], []
    df = df.sort_values("dt")
    recent = df[df["dt"] >= df["dt"].max() - pd.Timedelta(days=window_days)]
    if recent.empty:
        return [0.5, 0.3, 0.2], []
    y_true = recent["y"].astype(int).values
    feats_list = recent[feats].to_dict("records")
    best_w = [0.5, 0.3, 0.2]
    best_f1 = 0
    history = []
    for w0 in np.linspace(0, 1, 5):
        for w1 in np.linspace(0, 1-w0, 5):
            w2 = 1 - w0 - w1
            if w2 < 0 or w2 > 1:
                continue
            y_pred = []
            for f in feats_list:
                ml = _infer_ml(f)
                rule = _rule_based_score(f)
                vol = _volatility_score(f)
                score = w0*ml + w1*rule + w2*vol
                y_pred.append(int(score > 0.5))
            f1 = f1_score(y_true, y_pred)
            history.append({"weights": [w0, w1, w2], "f1": f1})
            if f1 > best_f1:
                best_f1 = f1
                best_w = [w0, w1, w2]
    return best_w, history

def auto_optimize(metric_drop_thresh=0.05, keep_last=5):
    if not Path(MODEL_HISTORY_PATH).exists():
        return
    with open(MODEL_HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)
    if len(history) < 2:
        return
    last = history[-1]
    prev = history[-2]
    if last["f1"] < prev["f1"] * (1 - metric_drop_thresh):
        import shutil
        prev_idx = prev.get("version", -1)
        backup_path = Path(f"data/models/signal_{prev_idx}.onnx")
        if backup_path.exists():
            shutil.copy(str(backup_path), str(Path("data/models/signal.onnx")))
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(prev, f)
        history = history[:-1]
        with open(MODEL_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history[-keep_last:], f)

def suggest_strategy_mix():
    from velayne.core.dataio import load_dataset
    df = load_dataset()
    mix = {}
    if df.empty or len(df) < 100:
        mix = {"recommendations": ["Включить больше данных для анализа."], "updated": pd.Timestamp.utcnow().isoformat()}
    else:
        last_pnls = df.groupby("strategy")["pnl"].mean().sort_values(ascending=False)
        mix["recommendations"] = []
        for strat, mean_pnl in last_pnls.items():
            if mean_pnl > 0:
                mix["recommendations"].append(f"✅ Стратегию {strat} оставить (PnL {mean_pnl:.2f})")
            else:
                mix["recommendations"].append(f"❌ Стратегию {strat} отключить (PnL {mean_pnl:.2f})")
        mix["updated"] = pd.Timestamp.utcnow().isoformat()
    with open(STRATEGY_MIX_PATH, "w", encoding="utf-8") as f:
        json.dump(mix, f)
    return mix