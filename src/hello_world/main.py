"""Entry point for the application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hello_world.database import Database
from hello_world.health import router as health_router
from hello_world.items import exceptions as item_exceptions
from hello_world.items import router as items_router
from hello_world.logger import get_logger
from hello_world.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Handle application lifespan events."""
    # Startup
    logger.info(
        "Application starting",
        environment=settings.environment,
        version=settings.app_version,
    )

    Database.initialize(settings)
    await Database.create_tables()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Application shutting down")
    await Database.close()
    logger.info("Database closed")


app = FastAPI(
    title="Hello World API",
    description="A production-ready FastAPI boilerplate with best practices",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers from items router (handlers defined in items/router.py for locality)
app.add_exception_handler(
    item_exceptions.ItemNotFoundError,
    items_router.item_not_found_handler,
)
app.add_exception_handler(
    item_exceptions.ItemValidationError,
    items_router.item_validation_error_handler,
)
app.add_exception_handler(
    item_exceptions.ItemAlreadyExistsError,
    items_router.item_already_exists_handler,
)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Hello World API",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(health_router.router)
app.include_router(items_router.router)


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "hello_world.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
        log_level="info",
    )
