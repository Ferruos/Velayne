"""
Blend manager: поддержка мультистратегий, весов, режимов рынка.
"""
import json

def blend_signals(signals: dict, weights: dict, mode: str = None):
    out = 0
    total_weight = 0
    for name, val in signals.items():
        w = weights.get(name, 1.0)
        out += w * val
        total_weight += abs(w)
    return out / (total_weight if total_weight else 1)

def select_regime(features: dict, model=None):
    # Простая логика: если нужна — ML модель
    # features = {'atr': ..., 'ma_slope': ..., ...}
    if features.get('ma_slope', 0) > 0.2:
        return "trend"
    elif features.get('atr', 0) > 0.03:
        return "panic"
    else:
        return "range"

def load_blend_config(path="blend.json"):
    with open(path, "r") as f:
        return json.load(f)

def save_blend_config(cfg, path="blend.json"):
    with open(path, "w") as f:
        json.dump(cfg, f)