"""Test fixtures for async test client."""

import os
from collections.abc import AsyncGenerator, Generator
from urllib.parse import urlparse, urlunparse

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from hello_world.database import Base, Database
from hello_world.main import app
from hello_world.settings import Settings, get_settings


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    """Provide a PostgreSQL connection URL from a testcontainer."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        sync_url = postgres.get_connection_url()
        parsed = urlparse(sync_url)
        async_url = urlunparse(
            (
                "postgresql+asyncpg",
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
        yield async_url


@pytest_asyncio.fixture()  # type: ignore[misc]
async def client(postgres_url: str) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with database."""
    os.environ["HELLO_WORLD_DATABASE_URL"] = postgres_url
    get_settings.cache_clear()

    settings = Settings()
    Database.initialize(settings)
    await Database.create_tables()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    await Database.close()


@pytest_asyncio.fixture()  # type: ignore[misc]
async def db_session(postgres_url: str) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for testing."""
    settings = Settings(database_url=postgres_url)
    Database.initialize(settings)
    await Database.create_tables()

    async for session in Database.get_session():
        yield session
        # Cleanup: delete all test data from all tables
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

    await Database.close()


pytest_plugins: list[str] = []
