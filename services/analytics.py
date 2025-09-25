import pandas as pd
from services.news import get_analyzed_news
import os

def get_full_analytics():
    blend_msg = "Blend: нет данных"
    trade_msg = "Торговля: нет данных"
    if os.path.exists("blend_metrics.csv"):
        blend_df = pd.read_csv("blend_metrics.csv")
        if not blend_df.empty:
            blend_summary = blend_df.tail(1).to_dict("records")[0]
            blend_msg = f"Blend: v{blend_summary.get('version','?')} Sharpe: {blend_summary.get('sharpe',0):.2f} Drawdown: {blend_summary.get('drawdown',0):.2%}"
    if os.path.exists("trade_stats.csv"):
        trades_df = pd.read_csv("trade_stats.csv")
        if not trades_df.empty:
            last_trade = trades_df.sort_values("timestamp").tail(1).to_dict("records")[0]
            pnl = trades_df["pnl"].sum()
            winrate = (trades_df["pnl"] > 0).mean()
            trade_msg = f"Торговля: PnL: {pnl:.2f} USDT, Winrate: {winrate:.1%}, Last: {last_trade['symbol']} {last_trade['pnl']} USDT"
    news = get_analyzed_news()
    news_msg = "\n".join([f"{n['title']} [{n['sentiment']}] ({n['score']:.2f})" for n in news])
    return f"{blend_msg}\n{trade_msg}\nНовости:\n{news_msg}"