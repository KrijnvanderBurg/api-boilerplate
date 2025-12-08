"""Main FastAPI application."""

from fastapi import FastAPI

from hello_world.api.routers import health, items

app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI boilerplate",
    version="0.1.0",
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(items.router, tags=["items"])
