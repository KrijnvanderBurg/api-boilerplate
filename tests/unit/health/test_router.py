"""Unit tests for health router."""

import os

import pytest

from hello_world.health.router import health_check, readiness_check
from hello_world.settings import get_settings


class TestHealthCheck:
    """Test health_check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check__returns_status_and_environment(self) -> None:
        """Test that health_check returns status and environment."""
        # Arrange
        os.environ["HELLO_WORLD_ENVIRONMENT"] = "test"
        get_settings.cache_clear()

        # Act
        result = await health_check()

        # Assert
        assert result["status"] == "healthy"
        assert "environment" in result


class TestReadinessCheck:
    """Test readiness_check endpoint."""

    @pytest.mark.asyncio
    async def test_readiness_check__returns_ready_status(self) -> None:
        """Test that readiness_check returns ready status."""
        # Act
        result = await readiness_check()

        # Assert
        assert result["status"] == "ready"
