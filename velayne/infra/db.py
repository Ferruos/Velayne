import os
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, select, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import NoSuchTableError, OperationalError
from sqlalchemy import inspect
from velayne.infra.config import get_settings

Base = declarative_base()
settings = get_settings()
DB_URL = settings.DB_URL

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sub_until = Column(DateTime, nullable=True)
    achievements = relationship("Achievement", back_populates="user")

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    amount = Column(Float)
    pnl = Column(Float)
    sandbox = Column(Boolean, default=True)

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key = Column(String)
    awarded_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="achievements")

engine = create_async_engine(DB_URL, echo=False, future=True)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    # Автообновление: добавление недостающих колонок/таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Автообновление колонок (только для SQLite)
        inspector = inspect(conn.sync_connection())
        # users.sub_until
        cols = [col["name"] for col in inspector.get_columns("users")]
        if "sub_until" not in cols:
            await conn.execute("ALTER TABLE users ADD COLUMN sub_until DATETIME")
        # achievements
        if not inspector.has_table("achievements"):
            await conn.run_sync(lambda c: Achievement.__table__.create(bind=c, checkfirst=True))

async def get_or_create_user(tg_id: int) -> User:
    async with async_session() as s:
        res = await s.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalars().first()
        if not user:
            user = User(tg_id=tg_id)
            s.add(user)
            await s.commit()
            await s.refresh(user)
        return user

async def get_user_sub_status(tg_id: int) -> dict:
    async with async_session() as s:
        res = await s.execute(select(User).where(User.tg_id == tg_id))
        user = res.scalars().first()
        if user and user.sub_until and user.sub_until > datetime.utcnow():
            return {"active": True, "until": user.sub_until}
        return {"active": False, "until": None}

async def list_users(limit: int = 100) -> list[dict]:
    async with async_session() as s:
        res = await s.execute(select(User).order_by(User.id.desc()).limit(limit))
        users = res.scalars().all()
        return [{"tg_id": u.tg_id, "sub_until": u.sub_until} for u in users]

async def get_last_trades(limit: int = 20) -> list[dict]:
    async with async_session() as s:
        res = await s.execute(select(Trade).order_by(Trade.id.desc()).limit(limit))
        trades = res.scalars().all()
        result = []
        for t in reversed(trades):
            # Автоконвертация ts если вдруг строка
            ts = t.ts
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts)
                except Exception:
                    ts = datetime.utcnow()
            result.append({
                "ts": ts.strftime("%d.%m.%Y %H:%M"),
                "symbol": t.symbol, "side": t.side, "price": t.price,
                "amount": t.amount, "pnl": t.pnl, "sandbox": t.sandbox
            })
        return result

async def append_trade_row(d: dict) -> None:
    async with async_session() as s:
        # ts может быть строкой или datetime
        ts = d.get("ts", datetime.utcnow())
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = datetime.utcnow()
        trade = Trade(
            ts=ts,
            symbol=d.get("symbol"),
            side=d.get("side"),
            price=d.get("price"),
            amount=d.get("amount"),
            pnl=d.get("pnl"),
            sandbox=d.get("sandbox", True)
        )
        s.add(trade)
        await s.commit()

async def get_live_stats() -> dict:
    async with async_session() as s:
        res = await s.execute(select(Trade.pnl))
        pnls = [r[0] for r in res.fetchall() if r[0] is not None]
        pnl_abs = sum(pnls) if pnls else 0.0
        trades = len(pnls)
        pnl_pct = pnl_abs / 10000 * 100 if trades else 0.0
        sharpe = (pnl_abs / (abs(pnl_abs) + 1e-8)) * 2 if trades else 0.0
        maxdd = min(pnls) if pnls else 0.0
        return dict(pnl_abs=pnl_abs, pnl_pct=pnl_pct, trades=trades, sharpe=sharpe, maxdd=maxdd)

async def award_achievement(user_id: int, key: str):
    async with async_session() as s:
        ach = Achievement(user_id=user_id, key=key)
        s.add(ach)
        await s.commit()

async def get_user_achievements(user_id: int):
    async with async_session() as s:
        res = await s.execute(select(Achievement).where(Achievement.user_id == user_id))
        return [a.key for a in res.scalars().all()]