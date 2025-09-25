"""
Light Market Making: выставляет лимитки возле средней цены, не агрессивно.
"""
import numpy as np

def market_making_signal(prices, spread=0.002):
    prices = np.array(prices)
    if len(prices) < 2:
        return 0, 0
    mid = prices[-1]
    buy_price = mid * (1 - spread)
    sell_price = mid * (1 + spread)
    return buy_price, sell_price