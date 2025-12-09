"""Database configuration and connection management."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from hello_world.settings import Settings, get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


class Database:
    """Database connection manager."""

    def __init__(self, settings: Settings) -> None:
        """Initialize database with settings.

        Args:
            settings: Application settings containing database configuration
        """
        self.engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
        )
        self.session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Generator[Session]:
        """Get database session.

        Yields:
            Session: SQLAlchemy database session
        """
        session = self.session_local()
        try:
            yield session
        finally:
            session.close()

    def close(self) -> None:
        """Close database connections."""
        self.engine.dispose()


def get_db(settings: Annotated[Settings, Depends(get_settings)]) -> Generator[Session]:
    """Get database session dependency.

    Args:
        settings: Application settings

    Yields:
        Session: SQLAlchemy database session
    """
    db = Database(settings)
    yield from db.get_session()
