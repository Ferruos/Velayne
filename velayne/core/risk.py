import numpy as np
from datetime import datetime, timedelta

def estimate_kelly(winrate, avg_win, avg_loss):
    """
    Kelly fraction = W - (1-W) * (avg_loss/avg_win)
    W: вероятность выигрыша
    avg_win: средний доход на выигрыш
    avg_loss: средний убыток (положительное число!)
    """
    if avg_win <= 0 or avg_loss <= 0:
        return 0.01  # минимальный размер
    k = winrate - (1 - winrate) * (avg_loss / avg_win)
    return max(0.01, min(k, 1.0))  # ограничить в [0.01, 1.0]

def position_size(pnl_history, balance, risk_profile):
    """
    Вычисляет оптимальный размер позиции по Kelly с учётом профиля риска.
    :param pnl_history: list[float] последних N сделок
    :param balance: float (текущий баланс)
    :param risk_profile: dict (risk_cap_fraction: float<=0.05)
    """
    N = min(len(pnl_history), 50)
    if N < 10 or balance <= 0:
        return balance * 0.01  # минимальный размер
    wins = [x for x in pnl_history[-N:] if x > 0]
    losses = [abs(x) for x in pnl_history[-N:] if x < 0]
    n_win = len(wins)
    n_loss = len(losses)
    winrate = n_win / N if N else 0.0
    avg_win = np.mean(wins) if wins else 1.0
    avg_loss = np.mean(losses) if losses else 1.0
    kelly = estimate_kelly(winrate, avg_win, avg_loss)
    cap = risk_profile.get("risk_cap_fraction", 0.05)  # например, 5% от баланса максимум
    pos_frac = min(kelly, cap)
    size = balance * pos_frac
    return max(size, balance * 0.01)

class DrawdownGovernor:
    def __init__(self, max_dd=0.15, min_size_frac=0.005, min_entry_interval=60):
        self.max_dd = max_dd
        self.min_size_frac = min_size_frac
        self.min_entry_interval = min_entry_interval  # в секундах
        self.high_watermark = None
        self.last_entry = None

    def check(self, balance, dt=None):
        if self.high_watermark is None or balance > self.high_watermark:
            self.high_watermark = balance
        dd = (self.high_watermark - balance) / self.high_watermark if self.high_watermark > 0 else 0.0
        restrict = False
        size_frac = 1.0
        entry_interval = 0
        if dd > self.max_dd:
            restrict = True
            size_frac = self.min_size_frac
            entry_interval = self.min_entry_interval
        return {
            "drawdown": dd,
            "restrict": restrict,
            "size_frac": size_frac,
            "entry_interval": entry_interval
        }

def apply_limits(signal, balance, risk_profile, pnl_history=None, governor=None, news_level=None):
    """
    signal: dict (action, symbol, size)
    balance: float
    risk_profile: dict
    pnl_history: list[float]
    governor: DrawdownGovernor
    """
    # Drawdown governor
    if governor:
        dd_info = governor.check(balance)
        if dd_info["restrict"]:
            signal["size"] = max(signal.get("size", balance * 0.01), balance * dd_info["size_frac"])
            # Можно добавить ограничение частоты входов по времени
            return signal

    # Position sizing by Kelly
    size = position_size(pnl_history or [], balance, risk_profile)
    if "size" in signal:
        signal["size"] = min(signal["size"], size)
    else:
        signal["size"] = size

    # Cap size по профилю риска
    max_frac = risk_profile.get("risk_cap_fraction", 0.05)
    max_size = balance * max_frac
    signal["size"] = min(signal["size"], max_size)
    # (по желанию: дополнительные фильтры по news_level etc)
    return signal

def get_profile(risk_mode):
    # Пример профилей риска
    profiles = {
        "safe": {"risk_cap_fraction": 0.02},
        "balanced": {"risk_cap_fraction": 0.05},
        "turbo": {"risk_cap_fraction": 0.1},
    }
    return profiles.get(risk_mode, profiles["safe"])

def check_circuit_breaker(pnl_day, profile):
    # Можно добавить circuit breaker по дневному убытку
    max_dd = profile.get("circuit_dd", 0.2)
    day_pnl = pnl_day.get("total", 0)
    if day_pnl < -abs(profile.get("balance", 10000)) * max_dd:
        return True
    return False