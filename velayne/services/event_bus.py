import asyncio
from dataclasses import dataclass
from typing import Literal, Any, Optional
from datetime import datetime

@dataclass
class TradeEvent:
    kind: Literal["trade"] = "trade"
    ts: datetime = datetime.utcnow()
    symbol: str = "BTC/USDT"
    side: Literal["buy", "sell"] = "buy"
    price: float = 0.0
    amount: float = 0.0
    pnl: Optional[float] = None
    sandbox: bool = True

@dataclass
class TrainingEvent:
    kind: Literal["training"] = "training"
    ts: datetime = datetime.utcnow()
    phase: Literal["start", "epoch", "end"] = "start"
    note: str = ""
    metrics: dict[str, Any] | None = None

@dataclass
class NewsEvent:
    kind: Literal["news"] = "news"
    ts: datetime = datetime.utcnow()
    title: str = ""
    url: str = ""
    sentiment: Optional[float] = None

@dataclass
class SubEvent:
    kind: Literal["sub"] = "sub"
    ts: datetime = datetime.utcnow()
    user_id: int = 0
    action: Literal["paid", "expired", "refund"] = "paid"
    until: Optional[datetime] = None
    amount: Optional[float] = None

# Глобальная очередь событий (в рамках процесса)
_event_queue: asyncio.Queue[Any] | None = None

def get_event_queue() -> asyncio.Queue[Any]:
    global _event_queue
    if _event_queue is None:
        _event_queue = asyncio.Queue(maxsize=1000)
    return _event_queue

async def publish(event: Any) -> None:
    q = get_event_queue()
    try:
        q.put_nowait(event)
    except asyncio.QueueFull:
        # Можно логировать переполнение очереди
        import logging
        logging.warning("[EVENT_BUS] Очередь событий заполнена, событие пропущено: %s", event)