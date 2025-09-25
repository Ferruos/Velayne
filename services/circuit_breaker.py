def circuit_breaker(user_id, user_metrics, drawdown_limit_pct=10):
    if abs(user_metrics.get("drawdown", 0)) > drawdown_limit_pct:
        # send alert, pause
        print(f"Циркут-брейкер: у пользователя {user_id} drawdown {user_metrics['drawdown']}% — автостоп!")
        return True
    return False