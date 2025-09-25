"""
Breakout strategy: генерирует сигналы на пробой диапазона.
"""
import numpy as np

def breakout_signal(prices, window=20):
    prices = np.array(prices)
    if len(prices) < window:
        return np.zeros_like(prices)
    recent = prices[-window:]
    high = np.max(recent)
    low = np.min(recent)
    signal = np.zeros(len(prices))
    if prices[-1] >= high:
        signal[-1] = 1  # Buy
    elif prices[-1] <= low:
        signal[-1] = -1 # Sell
    else:
        signal[-1] = 0
    return signal