@dp.message_handler(commands=["demo"])
async def demo(m: types.Message):
    # Включить демо-режим для пользователя
    await m.answer("Вам открыт демо-режим! Можно тестировать стратегии без риска.")