"""
Blend/strategy optimization via Optuna.
"""
import optuna
import numpy as np

def objective(trial, price_data):
    fast = trial.suggest_int("fast", 5, 20)
    slow = trial.suggest_int("slow", 10, 50)
    # Dummy backtest: difference between moving averages
    fast_ema = np.convolve(price_data, np.ones(fast)/fast, mode='valid')
    slow_ema = np.convolve(price_data, np.ones(slow)/slow, mode='valid')
    pnl = np.sum(fast_ema - slow_ema)
    return -np.abs(pnl)  # maximize absolute value

def run_optimization(price_data, n_trials=10):
    study = optuna.create_study(direction="minimize")
    study.optimize(lambda trial: objective(trial, price_data), n_trials=n_trials)
    return study.best_params