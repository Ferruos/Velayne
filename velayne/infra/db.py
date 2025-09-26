import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text, Enum, Float, func
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
import enum
import json
from cryptography.fernet import Fernet
import os

Base = declarative_base()

FERNET_KEY = os.getenv("FERNET_KEY", Fernet.generate_key())
fernet = Fernet(FERNET_KEY)

def encrypt(val):
    if val is None:
        return ""
    return fernet.encrypt(val.encode()).decode()

def decrypt(val):
    if not val:
        return ""
    return fernet.decrypt(val.encode()).decode()

class ExchangeEnum(enum.Enum):
    binance = "binance"
    bybit = "bybit"
    okx = "okx"

class StrategyDraftStatusEnum(enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"

class PortfolioKindEnum(enum.Enum):
    demo = "demo"
    live = "live"

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    exchange = Column(String, index=True)
    api_key_enc = Column(String, nullable=False)
    api_secret_enc = Column(String, nullable=False)
    passphrase_enc = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

class StrategyPreference(Base):
    __tablename__ = "strategy_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    enabled_codes = Column(JSON)
    last_recommended = Column(JSON)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class StrategyDraft(Base):
    __tablename__ = "strategy_drafts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    dsl_text = Column(Text)
    status = Column(Enum(StrategyDraftStatusEnum), default=StrategyDraftStatusEnum.submitted)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PublishedStrategy(Base):
    __tablename__ = "published_strategies"
    id = Column(Integer, primary_key=True)
    author_user_id = Column(Integer)
    code = Column(String, unique=True)
    name = Column(String)
    short_desc = Column(String)
    dsl_text = Column(Text)
    version = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_featured = Column(Boolean, default=False)

class BroadcastLog(Base):
    __tablename__ = "broadcast_log"
    id = Column(Integer, primary_key=True)
    author_user_id = Column(Integer, index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    total_targets = Column(Integer)
    sent_ok = Column(Integer)
    sent_fail = Column(Integer)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    event = Column(String)
    meta = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class PortfolioAccount(Base):
    __tablename__ = "portfolio_accounts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    kind = Column(Enum(PortfolioKindEnum), index=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    role = Column(String, default="user")  # 'user'|'editor'|'admin'
    created_at = Column(DateTime, default=func.now())

# --- Session/engine boilerplate ---
engine = create_async_engine("sqlite+aiosqlite:///data/velayne.db")
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

def upsert_api_key(session, user_id, exchange, api_key_plain, secret_plain, passphrase_plain=None):
    api_key_enc = encrypt(api_key_plain)
    secret_enc = encrypt(secret_plain)
    passphrase_enc = encrypt(passphrase_plain) if passphrase_plain else None
    obj = session.query(ApiKey).filter_by(user_id=user_id, exchange=exchange).first()
    if obj:
        obj.api_key_enc = api_key_enc
        obj.api_secret_enc = secret_enc
        obj.passphrase_enc = passphrase_enc
        obj.created_at = datetime.datetime.utcnow()
    else:
        obj = ApiKey(
            user_id=user_id, exchange=exchange,
            api_key_enc=api_key_enc, api_secret_enc=secret_enc,
            passphrase_enc=passphrase_enc
        )
        session.add(obj)
    session.commit()
    return obj

def get_user_api_key(session, user_id, exchange):
    obj = session.query(ApiKey).filter_by(user_id=user_id, exchange=exchange).first()
    if not obj:
        return None
    return (
        obj.exchange,
        decrypt(obj.api_key_enc),
        decrypt(obj.api_secret_enc),
        decrypt(obj.passphrase_enc) if obj.passphrase_enc else None
    )

def upsert_strategy_pref(session, user_id, enabled_codes, last_recommended):
    obj = session.query(StrategyPreference).filter_by(user_id=user_id).first()
    if obj:
        obj.enabled_codes = enabled_codes
        obj.last_recommended = last_recommended
        obj.updated_at = datetime.datetime.utcnow()
    else:
        obj = StrategyPreference(
            user_id=user_id,
            enabled_codes=enabled_codes,
            last_recommended=last_recommended,
        )
        session.add(obj)
    session.commit()
    return obj

def list_published_strategies(session):
    return session.query(PublishedStrategy).order_by(PublishedStrategy.is_featured.desc(), PublishedStrategy.updated_at.desc()).all()

def submit_strategy_draft(session, user_id, title, dsl_text):
    draft = StrategyDraft(
        user_id=user_id,
        title=title,
        dsl_text=dsl_text,
        status=StrategyDraftStatusEnum.submitted,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    session.add(draft)
    session.commit()
    return draft.id

def review_strategy_draft(session, draft_id, approve: bool, notes: str, publish_as: Optional[PublishedStrategy] = None):
    draft = session.query(StrategyDraft).filter_by(id=draft_id).first()
    if not draft:
        return False
    if approve:
        draft.status = StrategyDraftStatusEnum.approved
        if publish_as:
            session.add(publish_as)
    else:
        draft.status = StrategyDraftStatusEnum.rejected
    draft.notes = notes
    draft.updated_at = datetime.datetime.utcnow()
    session.commit()
    return True

def log_broadcast(author_user_id, message, total, ok, fail):
    session = SessionLocal()
    entry = BroadcastLog(
        author_user_id=author_user_id,
        message=message,
        created_at=datetime.datetime.utcnow(),
        total_targets=total,
        sent_ok=ok,
        sent_fail=fail
    )
    session.add(entry)
    session.commit()
    session.close()

def write_audit(event: str, meta: dict, user_id: int | None = None):
    session = SessionLocal()
    entry = AuditEvent(
        user_id=user_id,
        event=event,
        meta=meta,
        created_at=datetime.datetime.utcnow()
    )
    session.add(entry)
    session.commit()
    session.close()