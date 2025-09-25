"""
Генерирует PNG-отчет: баланс, PnL, сделки win/loss, разбивка по стратегиям blend.
"""
import matplotlib.pyplot as plt
import os

def make_daily_report(user_id, data, out_dir="reports/"):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(data["dates"], data["balance"], label="Balance", color="blue")
    ax.set_title(f"User {user_id} Daily Report")
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")
    ax.legend()
    # Добавим win/loss
    if "trades" in data:
        win = sum(1 for t in data["trades"] if t["pnl"] > 0)
        loss = sum(1 for t in data["trades"] if t["pnl"] <= 0)
        ax.text(0.02, 0.95, f"Wins: {win}, Losses: {loss}", transform=ax.transAxes)
    # Разбивка по стратегиям
    if "blend" in data:
        s = "\n".join([f"{k}: {v}" for k, v in data["blend"].items()])
        ax.text(0.7, 0.5, s, transform=ax.transAxes, bbox=dict(facecolor='yellow', alpha=0.2))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"report_{user_id}.png")
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)
    return path