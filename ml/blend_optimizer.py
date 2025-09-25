import optuna
from typing import Dict, Any, List

def optimize_blend(historical_data: List[Dict[str, Any]], strategy_classes, n_trials=5):
    def objective(trial):
        params = {}
        weights = []
        for strat_cls in strategy_classes:
            strat_params = {}
            for k in getattr(strat_cls, "param_space", []):
                strat_params[k] = trial.suggest_float(f"{strat_cls.name}_{k}", 1, 20) if "window" in k else trial.suggest_float(f"{strat_cls.name}_{k}", 0.01, 0.1)
            params[strat_cls.name] = strat_params
            weights.append(trial.suggest_float(f"weight_{strat_cls.name}", 0, 1))
        weights_sum = sum(weights)
        weights = [w / weights_sum for w in weights]
        return backtest(params, weights, historical_data, strategy_classes)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)
    best_params = study.best_trial.params
    components = []
    for i, strat_cls in enumerate(strategy_classes):
        strat_params = {k: best_params[f"{strat_cls.name}_{k}"] for k in getattr(strat_cls, "param_space", [])}
        weight = best_params[f"weight_{strat_cls.name}"]
        components.append({"name": strat_cls.name, "params": strat_params, "weight": weight})
    return {"components": components, "metrics": {"score": study.best_trial.value}}

def backtest(params, weights, historical_data, strategy_classes):
    # Фейковый бэктест: просто сумма случайных приростов
    return sum(weights) + 0.1  # Демо-значение