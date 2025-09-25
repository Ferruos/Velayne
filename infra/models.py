"""Database models for the Velayne application."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Float, Integer, String, Text, 
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    """User model for storing user information."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="user")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")
    api_keys: Mapped[list["ApiKey"]] = relationship("ApiKey", back_populates="user")
    workers: Mapped[list["Worker"]] = relationship("Worker", back_populates="user")
    event_logs: Mapped[list["EventLog"]] = relationship("EventLog", back_populates="user")
    achievements: Mapped[list["Achievement"]] = relationship("Achievement", back_populates="user")


class Subscription(Base):
    """Subscription model for user subscriptions."""
    
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    plan_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "basic", "premium", "pro"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")


class Payment(Base):
    """Payment model for tracking user payments."""
    
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, completed, failed, refunded
    payment_method: Mapped[str] = mapped_column(String(100), nullable=True)  # e.g., "yookassa", "card"
    external_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subscription_plan: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")


class Setting(Base):
    """Settings model for storing application and user settings."""
    
    __tablename__ = "settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)  # None for global settings
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(50), default="string")  # string, int, float, bool, json
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ApiKey(Base):
    """API keys model for storing encrypted trading API keys."""
    
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    exchange: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "binance", "bybit"
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # encrypted API key
    api_secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # encrypted API secret
    passphrase_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # encrypted passphrase for some exchanges
    is_testnet: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    permissions: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # comma-separated permissions
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")


class Worker(Base):
    """Worker model for tracking user trading workers/processes."""
    
    __tablename__ = "workers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    process_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # OS process ID
    status: Mapped[str] = mapped_column(String(50), default="stopped")  # stopped, starting, running, stopping, error
    mode: Mapped[str] = mapped_column(String(20), default="sandbox")  # sandbox, live
    strategy: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    risk_profile: Mapped[str] = mapped_column(String(50), default="balanced")  # safe, balanced, aggressive
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="workers")


class EventLog(Base):
    """Event log model for tracking user and system events."""
    
    __tablename__ = "event_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)  # None for system events
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "user_login", "payment_created", "worker_started"
    event_category: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "auth", "payment", "trading"
    severity: Mapped[str] = mapped_column(String(20), default="info")  # debug, info, warning, error, critical
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string with additional data
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="event_logs")


class Achievement(Base):
    """Achievement model for user achievements and milestones."""
    
    __tablename__ = "achievements"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    achievement_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "first_trade", "profit_milestone"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # emoji or icon identifier
    points: Mapped[int] = mapped_column(Integer, default=0)  # achievement points
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False)  # true for major milestones
    achievement_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string with achievement data
    earned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")