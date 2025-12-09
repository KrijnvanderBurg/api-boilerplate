"""Test fixtures for async test client.

Following FastAPI best practices, all integration tests should use
an async test client to avoid event loop issues.
"""

import os
from typing import Any, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from hello_world.database import Database
from hello_world.main import app
from hello_world.settings import get_settings


@pytest.fixture(scope="session")
def postgres_container():
    """Create a PostgreSQL container for testing.

    This fixture creates a PostgreSQL container that lives for the entire
    test session, providing a clean database for all tests.

    Yields:
        PostgresContainer: The running PostgreSQL container
    """
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="session")
def test_db(postgres_container: PostgresContainer) -> Generator[Database, Any, None]:
    """Create a test database using the PostgreSQL container.

    Args:
        postgres_container: The PostgreSQL container fixture

    Yields:
        Database: The test database instance
    """
    # Set the database URL from the container
    os.environ["HELLO_WORLD_DATABASE_URL"] = postgres_container.get_connection_url()

    # Clear the settings cache and get fresh settings with the new database URL
    get_settings.cache_clear()
    settings = get_settings()

    db = Database(settings)
    db.create_tables()
    yield db
    db.drop_tables()
    db.close()


@pytest_asyncio.fixture
async def client(test_db) -> Generator[AsyncClient, Any, None]:
    """Create an async test client for the API.

    This fixture provides an async httpx client for integration tests,
    following FastAPI best practices to avoid event loop issues.

    Args:
        test_db: The test database fixture

    Returns:
        AsyncClient: An async test client for making requests to the API
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    # Clean up database between tests
    test_db.drop_tables()
    test_db.create_tables()


pytest_plugins: list[str] = []
