from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tg_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class APIKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    exchange: str
    key_enc: str
    secret_enc: str

engine = create_engine("sqlite:///velayne.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)