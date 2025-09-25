"""Database configuration and session management using async SQLAlchemy."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from .config import settings

# Create the declarative base
Base = declarative_base()

# Global engine instance
engine: AsyncEngine = None
async_session_maker: async_sessionmaker[AsyncSession] = None


def create_engine() -> AsyncEngine:
    """
    Create and configure the async SQLAlchemy engine.
    
    Returns:
        Configured AsyncEngine instance
    """
    # SQLite-specific configuration for async operations
    engine_kwargs = {
        "echo": settings.debug,  # Log SQL queries in debug mode
        "future": True,
    }
    
    # Add SQLite-specific pool configuration
    if "sqlite" in settings.database_url:
        engine_kwargs.update({
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,
                # Force synchronous writes to ensure data is persisted
                "isolation_level": None,
            }
        })
    
    return create_async_engine(settings.database_url, **engine_kwargs)


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create the async session maker.
    
    Args:
        engine: AsyncEngine instance
        
    Returns:
        Configured async_sessionmaker
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False,
    )


def init_db():
    """Initialize the database engine and session maker."""
    global engine, async_session_maker
    
    if engine is None:
        engine = create_engine()
        async_session_maker = create_session_maker(engine)


async def create_tables():
    """Create all database tables."""
    if engine is None:
        init_db()
    
    # Use connect() and manual transaction management for better control
    async with engine.connect() as conn:
        async with conn.begin():
            await conn.run_sync(Base.metadata.create_all)
    
    # Force engine disposal to ensure all writes are flushed
    await engine.dispose()


async def drop_tables():
    """Drop all database tables."""
    if engine is None:
        init_db()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Yields:
        AsyncSession instance
    """
    if async_session_maker is None:
        init_db()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db():
    """Close the database engine."""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None


# Initialize database on import
init_db()