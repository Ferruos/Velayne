"""
Классификатор режима рынка: RandomForest (sklearn), обучение + предсказание.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

MODEL_PATH = "ml/regime_rf.pkl"

def extract_features(prices):
    # features: ATR, ма slope, std, returns
    prices = np.array(prices)
    returns = np.diff(prices) / prices[:-1]
    atr = np.mean(np.abs(np.diff(prices)))
    ma_slope = (prices[-1] - prices[0]) / len(prices)
    std = np.std(prices)
    return np.array([atr, ma_slope, std])

def fit_regime_model(price_series, labels):
    X = np.array([extract_features(p) for p in price_series])
    y = np.array(labels)
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    return clf

def predict_regime(prices):
    if not os.path.exists(MODEL_PATH):
        return "trend"  # fallback
    with open(MODEL_PATH, "rb") as f:
        clf = pickle.load(f)
    ftrs = extract_features(prices).reshape(1, -1)
    pred = clf.predict(ftrs)[0]
    return pred