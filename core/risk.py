def enforce_plan_caps(order, plan):
    if 'amount' in order and plan.max_order_size is not None:
        order['amount'] = min(order['amount'], plan.max_order_size)
    # Проверка числа позиций и баланса (можно добавить хранилище позиций)
    return order

def apply_stop_loss(order, user_metrics, stop_pct=-0.02):
    # Если дневной PnL ниже порога — не торгуем (или закрываем)
    if user_metrics.get('daily_pnl', 0.0) < stop_pct * user_metrics.get('balance', 1):
        order['action'] = "stop"
        order['amount'] = 0
    return order

def apply_trailing_stop(order, user_metrics, trailing_pct=0.01):
    # Можно хранить trailing_max, если PnL упал — закрыть
    if user_metrics.get('trailing_max', 0) - user_metrics.get('balance', 0) > trailing_pct * user_metrics.get('trailing_max', 1):
        order['action'] = "stop"
        order['amount'] = 0
    return order

def check_leverage(order, max_leverage=3):
    if order.get("leverage", 1) > max_leverage:
        order["leverage"] = max_leverage
    return order

def check_martingale(orders):
    # Запрет мартингейла: проверка удвоения объёма после лосса
    for i in range(1, len(orders)):
        if orders[i]['amount'] > orders[i-1]['amount'] * 1.5 and orders[i-1]['pnl'] < 0:
            return False
    return True