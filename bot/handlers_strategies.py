from aiogram import types

@dp.message_handler(commands=["strategies"])
async def show_strategies(m: types.Message):
    from core.strategies.marketplace import get_strategies
    strategies = get_strategies()
    text = "\n".join([f"{s['name']} (от {s['owner']}) — {s['desc']}" for s in strategies])
    await m.answer("Доступные стратегии:\n" + (text or "Нет стратегий"))

@dp.message_handler(commands=["addstrategy"])
async def add_strategy(m: types.Message):
    # В реальности: диалог для кода, параметров и описания
    code, params, desc = "...", {}, "..."
    from core.strategies.marketplace import add_strategy
    sid = add_strategy(m.from_user.id, "MyCustom", code, params, desc)
    await m.answer(f"Стратегия добавлена! ID: {sid}")