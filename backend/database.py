"""
Database connection management for CouncilOS.

Provides an async SQLAlchemy engine and session factory backed by PostgreSQL.
Falls back to SQLite for development/testing if DATABASE_URL is not set.
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./councilOS_dev.db",
)

# For SQLite async support, replace the driver if needed
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Dependency that yields an async database session."""
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """Create all tables. Used at application startup."""
    from models.blueprint import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose of the engine connection pool."""
    await engine.dispose()
