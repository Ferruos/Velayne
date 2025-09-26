from collections import defaultdict
from datetime import datetime, timedelta

class PnLTracker:
    def __init__(self):
        self.trades = []
        self.agg = defaultdict(list)
        self.max_drawdown = 0.0

    def get_aggregates(self, period: str) -> dict:
        now = datetime.utcnow()
        if period == 'day':
            since = now - timedelta(days=1)
        elif period == 'week':
            since = now - timedelta(weeks=1)
        elif period == 'month':
            since = now - timedelta(days=30)
        else:
            since = now - timedelta(days=1)
        trades = [t for t in self.trades if t['time'] >= since]
        pnl = sum(t['pnl'] for t in trades)
        win = sum(1 for t in trades if t['pnl'] > 0)
        loss = sum(1 for t in trades if t['pnl'] <= 0)
        winrate = win / (win + loss) if (win + loss) else 0
        avg_trade = pnl / len(trades) if trades else 0
        max_dd = min([t['cum_pnl'] for t in trades], default=0)
        return dict(
            total_pnl=pnl,
            winrate=winrate,
            avg_trade=avg_trade,
            max_drawdown=max_dd,
            trade_count=len(trades),
        )

    def on_fill(self, fill: dict):
        t = dict(fill)
        t['time'] = datetime.utcnow()
        t['pnl'] = fill.get('pnl', 0)
        last_cum = self.trades[-1]['cum_pnl'] if self.trades else 0
        t['cum_pnl'] = last_cum + t['pnl']
        self.trades.append(t)
        # update max DD
        min_cum = min(t['cum_pnl'] for t in self.trades)
        self.max_drawdown = min(self.max_drawdown, min_cum)

    def is_daily_dd_hit(self, profile) -> bool:
        dd = profile['max_daily_dd_pct'] / 100.0
        day_agg = self.get_aggregates('day')
        return day_agg['max_drawdown'] <= -dd