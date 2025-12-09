"""Test fixtures for async test client.

Following FastAPI best practices, all integration tests should use
an async test client to avoid event loop issues.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from hello_world.main import app


@pytest_asyncio.fixture
async def client():
    """Create an async test client for the API.

    This fixture provides an async httpx client for integration tests,
    following FastAPI best practices to avoid event loop issues.

    Returns:
        AsyncClient: An async test client for making requests to the API
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


pytest_plugins: list[str] = []
