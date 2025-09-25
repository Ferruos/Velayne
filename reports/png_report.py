import matplotlib.pyplot as plt
import numpy as np
import datetime, os

def make_daily_report(user_id, report_data):
    plt.figure(figsize=(8, 6))
    pnl = report_data.get('pnl', [])
    dates = report_data.get('dates', [])
    deals = report_data.get('deals', [])
    win = sum(1 for d in deals if d['pnl'] > 0)
    loss = sum(1 for d in deals if d['pnl'] <= 0)
    best = max(deals, key=lambda d: d['pnl'], default={})
    worst = min(deals, key=lambda d: d['pnl'], default={})
    by_strategy = report_data.get('by_strategy', {})
    plt.subplot(211)
    plt.plot(dates, pnl, label="PnL")
    plt.title(f"User {user_id} {datetime.date.today()} {report_data.get('mode','')}")
    plt.ylabel("Доходность")
    plt.legend()
    plt.subplot(212)
    plt.bar(list(by_strategy.keys()), list(by_strategy.values()))
    plt.title(f"Разбивка по стратегиям. Win: {win}, Loss: {loss}")
    plt.tight_layout()
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{user_id}_daily.png"
    plt.savefig(path)
    plt.close()
    return path