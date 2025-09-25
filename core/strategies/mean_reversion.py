"""
Mean Reversion strategy: генерирует сигналы на возврат к среднему.
"""
import numpy as np

def mean_reversion_signal(prices, window=20, threshold=2):
    prices = np.array(prices)
    if len(prices) < window:
        return np.zeros_like(prices)
    ma = np.convolve(prices, np.ones(window)/window, mode='valid')
    std = np.std(prices[-window:])
    signal = np.zeros(len(prices))
    zscore = (prices[-1] - ma[-1]) / (std + 1e-8)
    if zscore > threshold:
        signal[-1] = -1  # Sell
    elif zscore < -threshold:
        signal[-1] = 1   # Buy
    else:
        signal[-1] = 0
    return signal