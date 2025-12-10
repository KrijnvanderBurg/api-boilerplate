"""Database configuration and connection management."""

from collections.abc import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from hello_world.settings import Settings

# PostgreSQL naming conventions for indexes, constraints, etc.
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
    """Database connection manager using singleton pattern for engine."""

    _engine = None
    _session_maker = None

    @classmethod
    def initialize(cls, settings: Settings) -> None:
        """Initialize database engine once at startup."""
        if cls._engine is None:
            cls._engine = create_async_engine(
                settings.database_url,
                pool_pre_ping=True,
                echo=False,
            )
            cls._session_maker = async_sessionmaker(
                cls._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    @classmethod
    async def create_tables(cls) -> None:
        """Create all database tables."""
        if cls._engine is None:
            raise RuntimeError("Database not initialized")
        async with cls._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @classmethod
    async def close(cls) -> None:
        """Close database connections."""
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_maker = None

    @classmethod
    async def get_session(cls) -> AsyncGenerator[AsyncSession]:
        """Get database session.

        Yields:
            AsyncSession: SQLAlchemy async database session
        """
        if cls._session_maker is None:
            raise RuntimeError("Database not initialized")
        async with cls._session_maker() as session:
            yield session


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency for database session injection."""
    async for session in Database.get_session():
        yield session
