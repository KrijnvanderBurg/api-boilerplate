"""Entry point for the application."""

import uvicorn
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from hello_world.routers import health, items
from hello_world.settings import get_settings

# Get settings
settings = get_settings()

app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI boilerplate",
    version="0.1.0",
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(items.router, tags=["items"])

# Instrument FastAPI with OpenTelemetry
if settings.otel_enabled:
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health")


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "hello_world.__main__:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
