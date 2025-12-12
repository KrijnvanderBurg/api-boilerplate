"""Database configuration and connection management."""

from collections.abc import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from hello_world.logger import get_logger
from hello_world.settings import Settings

logger = get_logger(__name__)

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
            logger.debug("Initializing database engine", database_url=settings.database_url.split("@")[-1])
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
            logger.debug("Database engine initialized")
        else:
            logger.debug("Database engine already initialized")

    @classmethod
    async def create_tables(cls) -> None:
        """Create all database tables."""
        if cls._engine is None:
            logger.error("Attempted to create tables before database initialization")
            raise RuntimeError("Database not initialized")
        logger.debug("Creating database tables")
        async with cls._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.debug("Database tables created")

    @classmethod
    async def close(cls) -> None:
        """Close database connections."""
        if cls._engine:
            logger.debug("Closing database connections")
            await cls._engine.dispose()
            cls._engine = None
            cls._session_maker = None
            logger.debug("Database connections closed")
        else:
            logger.debug("No database connections to close")

    @classmethod
    async def get_session(cls) -> AsyncGenerator[AsyncSession]:
        """Get database session.

        Yields:
            AsyncSession: SQLAlchemy async database session
        """
        if cls._session_maker is None:
            logger.error("Attempted to get session before database initialization")
            raise RuntimeError("Database not initialized")
        logger.debug("Creating new database session")
        async with cls._session_maker() as session:
            yield session
        logger.debug("Database session closed")


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency for database session injection."""
    logger.debug("Providing database session via dependency injection")
    async for session in Database.get_session():
        yield session
