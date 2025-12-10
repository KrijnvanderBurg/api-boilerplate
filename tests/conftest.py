"""Test fixtures for async test client.

Following FastAPI best practices, all integration tests should use
an async test client to avoid event loop issues.
"""

import os
from collections.abc import AsyncGenerator, Generator
from urllib.parse import urlparse, urlunparse

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from hello_world.database import Database
from hello_world.main import app
from hello_world.settings import Settings, get_settings


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    """Provide a PostgreSQL connection URL from a testcontainer.

    The container runs for the entire test session and is automatically
    cleaned up when the session ends.

    Yields:
        str: Async PostgreSQL connection URL
    """
    with PostgresContainer("postgres:16-alpine") as postgres:
        # Parse the URL and reconstruct with asyncpg driver
        sync_url = postgres.get_connection_url()
        parsed = urlparse(sync_url)

        # Reconstruct URL with asyncpg driver for async operations
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


@pytest_asyncio.fixture()
async def client(postgres_url: str) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with a fresh database for each test.

    Each test gets its own isolated database instance to prevent test
    interference while sharing the same PostgreSQL container.

    Args:
        postgres_url: PostgreSQL connection URL from testcontainer

    Yields:
        AsyncClient: HTTP client for testing the API
    """
    # Configure database URL for this test
    os.environ["HELLO_WORLD_DATABASE_URL"] = postgres_url
    get_settings.cache_clear()

    # Initialize database
    settings = Settings()
    Database.initialize(settings)
    await Database.create_tables()

    # Create and yield test client
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    # Cleanup database
    await Database.close()


pytest_plugins: list[str] = []
