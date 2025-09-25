from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    tg_id: int
    terms_accepted: bool
    created_at: datetime.datetime

class Subscription(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    plan: str
    expires_at: datetime.datetime
    status: str

class APICredential(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    exchange: str
    key_enc: str
    secret_enc: str
    passphrase_enc: Optional[str]

class BlendVersion(SQLModel, table=True):
    id: int = Field(primary_key=True)
    version: str
    json_params: str
    created_at: datetime.datetime
    metrics: Optional[str]

class Session(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    blend_version: str
    risk_profile: str
    started_at: datetime.datetime
    status: str

class Run(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    session_id: int
    pnl: float
    drawdown: float
    metrics: str

class Order(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    symbol: str
    side: str
    size: float
    price: float
    pnl: float
    status: str
    created_at: datetime.datetime

class Trade(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    symbol: str
    side: str
    size: float
    price: float
    commission: float
    created_at: datetime.datetime

class Payment(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int
    plan: str
    provider: str
    timestamp: datetime.datetime
    status: str