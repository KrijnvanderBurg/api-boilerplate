"""End-to-end tests using testcontainers for full application stack.

This test module spins up actual Docker containers:
- PostgreSQL database container
- FastAPI application container

Tests verify real HTTP requests to the containerized application.
"""

import time
from collections.abc import Generator

import httpx
import pytest
from testcontainers.core.container import DockerContainer  # type: ignore[import-untyped]
from testcontainers.core.network import Network  # type: ignore[import-untyped]
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]


@pytest.fixture(scope="module")
def api_client(e2e_postgres: PostgresContainer) -> Generator[str, None, None]:
    """Provide API base URL with postgres and app connected on network.

    Note: Uses e2e_postgres from conftest which is module-scoped. Network teardown
    may show an error about active endpoints, but this is harmless - the test passes
    and containers are cleaned up properly.
    """
    with Network() as network:
        network.connect(e2e_postgres.get_wrapped_container().id)

        postgres_url = (
            f"postgresql+asyncpg://{e2e_postgres.username}:{e2e_postgres.password}"
            f"@{e2e_postgres.get_wrapped_container().name}:{e2e_postgres.port}/{e2e_postgres.dbname}"
        )

        with (
            DockerContainer(image="hello-world-api:test")
            .with_env("HELLO_WORLD_DATABASE_URL", postgres_url)
            .with_env("HELLO_WORLD_LOG_LEVEL", "info")
            .with_env("HELLO_WORLD_ENVIRONMENT", "test")
            .with_env("HELLO_WORLD_APP_VERSION", "test")
            .with_env("HELLO_WORLD_SERVER_HOST", "0.0.0.0")
            .with_env("HELLO_WORLD_SERVER_PORT", "8000")
            .with_env("HELLO_WORLD_CORS_ORIGINS", "[]")
            .with_exposed_ports(8000)
        ) as app_container:
            network.connect(app_container.get_wrapped_container().id)

            port = app_container.get_exposed_port(8000)
            base_url = f"http://localhost:{port}"

            # Wait for app to be ready
            for attempt in range(60):
                try:
                    response = httpx.get(f"{base_url}/health", timeout=2.0)
                    if response.status_code == 200:
                        break
                except Exception:
                    if attempt == 59:
                        logs = app_container.get_logs()
                        print(f"Container logs:\nSTDOUT:\n{logs[0].decode()}\nSTDERR:\n{logs[1].decode()}")
                        raise
                    time.sleep(1)

            yield base_url


class TestItemsE2E:
    """End-to-end tests for items API using Docker containers."""

    @pytest.mark.asyncio
    async def test_create_and_read_item(self, api_client: str) -> None:
        """Test creating an item via POST and retrieving it via GET."""
        async with httpx.AsyncClient(base_url=api_client, timeout=10.0) as client:
            # Create item
            item_data = {
                "name": "E2E Test Item",
                "description": "Created in end-to-end test",
                "price": 42.99,
            }
            create_response = await client.post("/items", json=item_data)

            assert create_response.status_code == 201
            created_item = create_response.json()
            assert created_item["name"] == item_data["name"]
            assert created_item["description"] == item_data["description"]
            assert created_item["price"] == item_data["price"]
            assert "id" in created_item

            # Read the created item
            item_id = created_item["id"]
            read_response = await client.get(f"/items/{item_id}")

            assert read_response.status_code == 200
            retrieved_item = read_response.json()
            assert retrieved_item["id"] == item_id
            assert retrieved_item["name"] == item_data["name"]
            assert retrieved_item["description"] == item_data["description"]
            assert retrieved_item["price"] == item_data["price"]
