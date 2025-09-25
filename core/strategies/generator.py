"""
Генератор стратегий: на основе описания пользователя или выбора preset.
"""
def generate_strategy_from_prompt(prompt):
    if "скальп" in prompt.lower():
        code = """def generate_signal(market_data): ... # scalp logic"""
        params = {"window": 5}
        desc = "Скальпинг-стратегия."
        return code, params, desc
    elif "breakout" in prompt.lower():
        code = """def generate_signal(market_data): ... # breakout logic"""
        params = {"window": 20}
        desc = "Автоматически сгенерированная breakout-стратегия."
        return code, params, desc
    # ...добавить свои шаблоны...
    return None, None, "Не удалось сгенерировать стратегию."