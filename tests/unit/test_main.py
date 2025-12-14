"""Unit tests for main application module."""

import importlib
import os

import pytest
from sqlalchemy import text

import hello_world.main
from hello_world.database import Database
from hello_world.main import root
from hello_world.settings import get_settings


class TestLifespan:
    """Test lifespan context manager using real database."""

    @pytest.mark.asyncio
    async def test_lifespan__initializes_and_closes_database(
        self,
        postgres_url: str,
    ) -> None:
        """Test that lifespan initializes database on startup and closes on shutdown."""
        # Arrange - Set environment before importing main module
        os.environ["HELLO_WORLD_DATABASE_URL"] = postgres_url

        # Force reload of settings and main module to pick up new environment
        get_settings.cache_clear()
        importlib.reload(hello_world.main)

        # Reimport after reload
        from hello_world.main import app as reloaded_app
        from hello_world.main import lifespan as reloaded_lifespan

        # Act & Assert - Run the lifespan context manager
        async with reloaded_lifespan(reloaded_app):
            # During lifespan, database should be initialized
            # Verify database is initialized by getting a session
            session_gen = Database.get_session()
            session = await session_gen.__anext__()
            try:
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
            finally:
                await session_gen.aclose()

        # After lifespan exits, cleanup happens automatically


class TestRootEndpoint:
    """Test root endpoint."""

    @pytest.mark.asyncio
    async def test_root__returns_api_information(self) -> None:
        """Test that root endpoint returns API information."""
        # Act
        result = await root()

        # Assert
        assert result["message"] == "Hello World API"
        assert "version" in result
        assert "environment" in result
        assert "health" in result["endpoints"]
        assert "items" in result["endpoints"]

    @pytest.mark.asyncio
    async def test_root__includes_all_endpoints(self) -> None:
        """Test that root endpoint includes all expected endpoints."""
        # Act
        result = await root()

        # Assert
        items_endpoints = result["endpoints"]["items"]
        assert "read_items" in items_endpoints
        assert "create_item" in items_endpoints
        assert "read_item" in items_endpoints
        assert "update_item" in items_endpoints
        assert "delete_item" in items_endpoints

        # Verify health endpoint
        health_endpoint = result["endpoints"]["health"]
        assert health_endpoint["url"] == "/health"
        assert health_endpoint["method"] == "GET"
