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

    @pytest.mark.asyncio
    async def test_health_check__with_production_environment__returns_production(self) -> None:
        """Test that health_check returns production environment."""
        # Arrange
        os.environ["HELLO_WORLD_ENVIRONMENT"] = "production"
        get_settings.cache_clear()

        # Act
        result = await health_check()

        # Assert
        assert result["status"] == "healthy"
        assert result["environment"] == "production"

    @pytest.mark.asyncio
    async def test_health_check__with_development_environment__returns_development(self) -> None:
        """Test that health_check returns development environment."""
        # Arrange
        os.environ["HELLO_WORLD_ENVIRONMENT"] = "development"
        get_settings.cache_clear()

        # Act
        result = await health_check()

        # Assert
        assert result["status"] == "healthy"
        assert result["environment"] == "development"

    @pytest.mark.asyncio
    async def test_health_check__without_environment__returns_none(self) -> None:
        """Test that health_check handles missing environment gracefully."""
        # Arrange
        if "HELLO_WORLD_ENVIRONMENT" in os.environ:
            del os.environ["HELLO_WORLD_ENVIRONMENT"]
        get_settings.cache_clear()

        # Act
        result = await health_check()

        # Assert
        assert result["status"] == "healthy"
        assert result["environment"] == "None"

    @pytest.mark.asyncio
    async def test_health_check__always_returns_healthy_status(self) -> None:
        """Test that health_check always returns healthy status."""
        # Arrange
        os.environ["HELLO_WORLD_ENVIRONMENT"] = "staging"
        get_settings.cache_clear()

        # Act
        result = await health_check()

        # Assert
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check__returns_dict_with_required_keys(self) -> None:
        """Test that health_check returns dict with required keys."""
        # Arrange
        os.environ["HELLO_WORLD_ENVIRONMENT"] = "test"
        get_settings.cache_clear()

        # Act
        result = await health_check()

        # Assert
        assert isinstance(result, dict)
        assert "status" in result
        assert "environment" in result
        assert len(result) == 2


class TestReadinessCheck:
    """Test readiness_check endpoint."""

    @pytest.mark.asyncio
    async def test_readiness_check__returns_ready_status(self) -> None:
        """Test that readiness_check returns ready status."""
        # Act
        result = await readiness_check()

        # Assert
        assert result["status"] == "ready"
