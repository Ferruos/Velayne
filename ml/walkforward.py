"""
Walk-forward валидация для отбора стратегий/blend.
"""
def walk_forward_validate(param_sets, historical_data, strategy_classes):
    best_score = float("-inf")
    best_params = None
    for params in param_sets:
        score = backtest(params, historical_data, strategy_classes)
        if score > best_score:
            best_score = score
            best_params = params
    return best_params, best_score

def backtest(params, historical_data, strategy_classes):
    # Мок: сумма весов
    return sum(p.get("weight", 1) for p in params.values())