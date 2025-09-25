"""
EMA strategy, signal generator. Возвращает 1 (long), -1 (short), 0 (нет сигнала)
"""
import numpy as np

def ema_signal(prices, fast=12, slow=26):
    prices = np.array(prices)
    if len(prices) < max(fast, slow):
        return np.zeros_like(prices)
    fast_ema = np.convolve(prices, np.ones(fast)/fast, mode='valid')
    slow_ema = np.convolve(prices, np.ones(slow)/slow, mode='valid')
    signal = np.zeros(len(prices))
    if fast_ema[-1] > slow_ema[-1]:
        signal[-1] = 1
    elif fast_ema[-1] < slow_ema[-1]:
        signal[-1] = -1
    else:
        signal[-1] = 0
    return signal