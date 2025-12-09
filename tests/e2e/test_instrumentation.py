"""E2E tests for OpenTelemetry instrumentation."""

import subprocess
import time

import httpx
import pytest


@pytest.fixture(scope="module")
def instrumented_app():
    """Start the app with OpenTelemetry instrumentation."""
    env = {
        "OTEL_SERVICE_NAME": "hello-world-api",
        "OTEL_TRACES_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://otel-collector:4318",
        "OTEL_METRICS_EXPORTER": "none",
        "OTEL_LOGS_EXPORTER": "none",
    }

    proc = subprocess.Popen(
        ["opentelemetry-instrument", "python", "-m", "hello_world"],
        env={**subprocess.os.environ, **env},
    )

    # Wait for startup
    time.sleep(3)

    yield

    proc.terminate()
    proc.wait(timeout=5)


@pytest.mark.asyncio
async def test_instrumented_health_endpoint(instrumented_app):
    """Test that instrumented app responds correctly."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_instrumented_items_endpoint(instrumented_app):
    """Test that instrumented items endpoint works."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/items")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
