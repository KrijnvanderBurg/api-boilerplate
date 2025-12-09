"""Database configuration and connection management."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from hello_world.settings import Settings, get_settings

# PostgreSQL naming conventions for indexes, constraints, etc.
# This ensures consistent naming across migrations and database objects
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class Database:
    """Async database connection manager."""

    def __init__(self, settings: Settings) -> None:
        """Initialize database with settings.

        Args:
            settings: Application settings containing database configuration
        """
        self.engine = create_async_engine(
            settings.database_url,
            pool_pre_ping=True,
            echo=False,
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session.

        Yields:
            AsyncSession: SQLAlchemy async database session
        """
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()


async def get_db(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    This dependency creates a new Database instance per request with its own
    connection pool. FastAPI's dependency injection ensures proper lifecycle
    management without needing global state.

    Args:
        settings: Application settings

    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    db = Database(settings)
    async for session in db.get_session():
        yield session
    await db.close()
