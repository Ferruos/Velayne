"""
Volatility strategy: заходит только в моменты резкого всплеска волатильности.
"""
import numpy as np

def volatility_signal(prices, window=14, threshold=0.03):
    prices = np.array(prices)
    if len(prices) < window + 1:
        return np.zeros_like(prices)
    returns = np.diff(prices[-(window+1):]) / prices[-(window+1):-1]
    vol = np.std(returns)
    signal = np.zeros(len(prices))
    if vol > threshold:
        signal[-1] = 1  # Signal to act (например, Buy)
    else:
        signal[-1] = 0
    return signal