"""
Walk-forward валидация и drift detection для blend.
"""
import numpy as np
from ml.optimizer import run_optimization

def walk_forward_opt(prices, window=200, step=50):
    best_params = []
    for i in range(window, len(prices), step):
        train = prices[i-window:i]
        params = run_optimization(train, n_trials=10)
        best_params.append(params)
    return best_params

def detect_drift(metrics_hist, threshold=0.1):
    # Простой drift: если последние 5 pnl < средних прошлых
    if len(metrics_hist) < 10:
        return False
    recent = metrics_hist[-5:]
    past = metrics_hist[:-5]
    if np.mean(recent) < np.mean(past)*(1-threshold):
        return True
    return False