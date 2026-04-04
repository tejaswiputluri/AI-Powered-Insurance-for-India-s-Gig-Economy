"""
GigShield Database — SQLAlchemy async engine + session factory.
Supports PostgreSQL (Supabase) and SQLite for local development.
"""

import logging
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Determine if we're using SQLite
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Engine configuration
engine_kwargs = {
    "echo": settings.APP_ENV == "development",
}

# PostgreSQL needs pool settings; SQLite doesn't support them
if not _is_sqlite:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
else:
    from sqlalchemy.pool import StaticPool
    engine_kwargs["poolclass"] = StaticPool

# For SQLite, we need connect_args to allow multi-threaded usage
if _is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables. Called on app startup."""
    # Import all models so SQLAlchemy discovers them
    import backend.models.db  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db_type = "SQLite" if _is_sqlite else "PostgreSQL"
    logger.info(f"✅ Database initialized ({db_type})")


async def close_db():
    """Dispose engine. Called on app shutdown."""
    await engine.dispose()
