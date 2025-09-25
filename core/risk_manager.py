"""
Risk manager: дневной стоп, enforce_plan_caps, плечо, запрет мартингейла, трейлинг-стоп.
"""
from core.plan_limits import PLANS

class RiskManager:
    def __init__(self, plan, daily_loss_limit=-0.02, max_leverage=2):
        self.plan = plan
        self.daily_loss_limit = daily_loss_limit
        self.max_leverage = max_leverage
        self.daily_start_balance = None
        self.trail_price = None

    def check_daily_stop(self, start_balance, curr_balance):
        if self.daily_start_balance is None:
            self.daily_start_balance = start_balance
        loss = (curr_balance - self.daily_start_balance) / self.daily_start_balance
        return loss > self.daily_loss_limit  # True если превышен лимит

    def enforce_caps(self, balance, order_size, open_positions):
        caps = PLANS[self.plan]
        new_order_size = min(order_size, caps["max_order"])
        if balance > caps["max_balance"]:
            new_order_size = min(new_order_size, caps["max_balance"])
        allowed = open_positions < caps["max_open_positions"]
        return new_order_size, allowed

    def clamp_leverage(self, requested_leverage):
        return min(requested_leverage, self.max_leverage)

    def forbid_martingale(self, last_order_size, next_order_size):
        return next_order_size <= last_order_size * 1.1  # Запрет на мартингейл

    def trailing_stop(self, price, trailing_pct=0.01):
        if self.trail_price is None or price > self.trail_price:
            self.trail_price = price
        return price < self.trail_price * (1 - trailing_pct)