import numpy as np
import optuna
from typing import Dict, Any, List

def optimize_blend(historical_data: List[Dict[str, Any]], strategy_classes,
                   n_trials: int = 5):
    """
    Подбирает параметры и веса стратегий через Optuna.
    """
    def objective(trial):
        params = {}
        weights = []
        # Перебираем все классы стратегий и запрашиваем параметры из их param_space
        for strat_cls in strategy_classes:
            strat_params = {}
            for k in getattr(strat_cls, "param_space", []):
                # окна — целые числа, остальные параметры — float
                if "window" in k:
                    strat_params[k] = trial.suggest_int(f"{strat_cls.name}_{k}", 2, 50)
                else:
                    strat_params[k] = trial.suggest_float(f"{strat_cls.name}_{k}", 0.01, 0.5)
            params[strat_cls.name] = strat_params
            weights.append(trial.suggest_float(f"weight_{strat_cls.name}", 0.0, 1.0))
        # Нормализуем веса, чтобы сумма = 1
        wsum = sum(weights) + 1e-12
        norm_weights = [w / wsum for w in weights]
        return backtest(params, norm_weights, historical_data, strategy_classes)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    best_params = study.best_trial.params

    components = []
    for idx, strat_cls in enumerate(strategy_classes):
        strat_params = {k: best_params[f"{strat_cls.name}_{k}"]
                        for k in getattr(strat_cls, "param_space", [])}
        weight = best_params[f"weight_{strat_cls.name}"]
        components.append({"name": strat_cls.name,
                           "params": strat_params,
                           "weight": weight})
    return {"components": components,
            "metrics": {"score": study.best_trial.value}}

def backtest(params: Dict[str, Dict[str, Any]], weights: List[float],
             historical_data: List[Dict[str, Any]], strategy_classes):
    """
    Простейший бэктест:
    - Для каждой свечи вычисляем сигнал каждой стратегии (buy/sell/hold).
    - Конвертируем сигнал в +1/-1/0, умножаем на вес стратегии.
    - Домножаем на процентное изменение цены между свечами.
    - Возвращаем отношение средней доходности к её стандартному отклонению.
    """
    prices = historical_data[0]["close"]
    returns = []
    for t in range(1, len(prices)):
        price_change = (prices[t] - prices[t-1]) / prices[t-1]
        weighted_signal = 0.0
        # генерируем сигнал каждой стратегии на исторических данных до текущей точки
        for idx, strat_cls in enumerate(strategy_classes):
            strat_params = params.get(strat_cls.name, {})
            strat_instance = strat_cls(strat_params)
            market_slice = {"close": prices[:t]}  # до t‑й свечи включительно
            signal = strat_instance.generate_signal(market_slice)
            action = signal.get("action", "hold")
            sign = 1 if action == "buy" else -1 if action == "sell" else 0
            weighted_signal += weights[idx] * sign
        returns.append(weighted_signal * price_change)
    if not returns:
        return -1e9  # защитим Optuna от деления на ноль
    mean_ret = float(np.mean(returns))
    std_ret = float(np.std(returns) + 1e-12)
    return mean_ret / std_ret
