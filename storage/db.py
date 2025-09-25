from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tg_id: int
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine("sqlite:///velayne.db")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)