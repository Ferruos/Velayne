from core.blend.blend_manager import BlendManager
from core.risk import enforce_plan_caps, apply_trailing_stop, apply_stop_loss
from core.strategies import STRATEGY_CLASSES

class PortfolioManager:
    def __init__(self, blend_manager: BlendManager, plan):
        self.blend_manager = blend_manager
        self.plan = plan

    def aggregate_signals(self, user_id, market_data, user_metrics=None):
        blend = self.blend_manager.get_current_blend()
        signals = []
        for strat_cfg in blend['components']:
            strat_class = self._resolve_strategy_class(strat_cfg['name'])
            strat = strat_class(strat_cfg['params'])
            signal = strat.generate_signal(market_data)
            signals.append((strat_cfg['weight'], signal))

        agg_action, agg_size = self._blend_signals(signals)
        order = {"action": agg_action, "amount": agg_size}
        order = enforce_plan_caps(order, self.plan)
        if user_metrics:
            order = apply_trailing_stop(order, user_metrics)
            order = apply_stop_loss(order, user_metrics)
        return order

    def _blend_signals(self, signals):
        buy_votes = sum(w for w, s in signals if s.get("action") == "buy")
        sell_votes = sum(w for w, s in signals if s.get("action") == "sell")
        amount = max(buy_votes, sell_votes) / (sum(w for w, _ in signals) + 1e-9) * (self.plan.max_order_size or 0.01)
        if buy_votes > sell_votes:
            return "buy", amount
        elif sell_votes > buy_votes:
            return "sell", amount
        else:
            return "hold", 0.0

    def _resolve_strategy_class(self, name):
        for cls in STRATEGY_CLASSES:
            if cls.name == name:
                return cls
        raise ValueError(f"Unknown strategy: {name}")