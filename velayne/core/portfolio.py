from typing import Dict, Any
from datetime import datetime

class Portfolio:
    def __init__(self, init_balance=10000):
        self.accounts = {
            "demo": {"balance": init_balance, "positions": {}, "history": [], "created_at": datetime.utcnow()},
            "live": {"balance": 0.0, "positions": {}, "history": [], "created_at": datetime.utcnow()},
        }

    def get_state(self):
        return self.accounts

    def update_on_fill(self, fill: dict, kind: str = "demo"):
        acc = self.accounts[kind]
        acc["history"].append(fill)
        pnl = fill.get("pnl", 0.0)
        fee = fill.get("fee", 0.0)
        size = fill.get("size", 0.0)
        if fill.get("side", "buy") == "buy":
            acc["balance"] -= (size * fill.get("price", 0.0)) + fee
        else:
            acc["balance"] += (size * fill.get("price", 0.0)) - fee
        acc["balance"] += pnl

    def reset_daily_limits(self):
        # Optional: enforce daily risk limits etc
        pass

    def can_open(self, symbol, size, kind="demo"):
        # Dummy: always allow
        return True

    def aggregate_summary(self):
        res = {}
        for k, acc in self.accounts.items():
            res[k] = {
                "balance": acc["balance"],
                "positions": dict(acc["positions"]),
                "n_trades": len(acc["history"]),
                "created_at": acc.get("created_at"),
            }
        # Дополнительно: общий баланс, PnL, etc
        res["total_balance"] = sum(acc["balance"] for acc in self.accounts.values())
        return res