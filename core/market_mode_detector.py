"""
ML-модель: определение режима рынка (trend/range/panic) по индикаторам.
"""
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class MarketModeDetector:
    def __init__(self):
        self.clf = RandomForestClassifier(n_estimators=10)
        self.is_fitted = False

    def fit(self, X, y):
        self.clf.fit(X, y)
        self.is_fitted = True

    def predict(self, features: dict):
        X = np.array([list(features.values())])
        label = self.clf.predict(X)[0] if self.is_fitted else "trend"
        return label

def extract_features(market_data):
    prices = np.array(market_data["close"])
    returns = np.diff(prices) / prices[:-1]
    atr = np.std(returns)
    slope = (prices[-1] - prices[0]) / len(prices)
    corr = np.corrcoef(prices[:-1], prices[1:])[0, 1]
    features = {
        "atr": atr,
        "slope": slope,
        "corr": corr,
    }
    return features