import asyncio
from datetime import datetime
from velayne.services.event_bus import publish, TradeEvent
from velayne.infra.config import is_sandbox_mode
from velayne.infra.db import append_trade_row

async def start_sandbox_service():
    """
    Главная точка входа для sandbox/live движка.
    Симуляция торговли — создаёт сделки каждые 10 секунд.
    """
    while True:
        symbol = "BTC/USDT"
        side = "buy"
        price = 50000.0
        amount = 0.01
        pnl_value = 10.0
        sandbox = is_sandbox_mode()
        trade_data = {
            "ts": datetime.utcnow(),
            "symbol": symbol,
            "side": side,
            "price": price,
            "amount": amount,
            "pnl": pnl_value,
            "sandbox": int(sandbox)
        }
        await publish(TradeEvent(
            symbol=symbol,
            side=side,
            price=price,
            amount=amount,
            pnl=pnl_value,
            sandbox=sandbox
        ))
        await append_trade_row(trade_data)
        await asyncio.sleep(10)