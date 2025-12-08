"""Entry point for the application."""

import uvicorn
from fastapi import FastAPI

from hello_world.routers import health, items

app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI boilerplate",
    version="0.1.0",
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(items.router, tags=["items"])


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "hello_world.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
