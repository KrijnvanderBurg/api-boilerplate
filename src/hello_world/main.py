"""Entry point for the application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from hello_world.database import Database
from hello_world.health import router as health_router
from hello_world.items import exceptions as item_exceptions
from hello_world.items import router as items_router
from hello_world.settings import get_settings
from hello_world.utils import logger as logger_utils

settings = get_settings()
logger = logger_utils.get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Handle application lifespan events.

    This context manager handles startup and shutdown events for the application.
    Use this to initialize resources on startup and clean them up on shutdown.

    Yields:
        None: Control during the application's lifetime
    """
    # Startup
    logger.info(
        "Application starting",
        environment=settings.environment,
        version=settings.app_version,
    )

    # Initialize database
    db = Database(settings)
    db.create_tables()
    logger.info("Database initialized", database_url=settings.database_url)

    yield

    # Shutdown
    logger.info("Application shutting down")
    db.close()
    logger.info("Database connections closed")


app = FastAPI(
    title="Hello World API",
    description="A production-ready FastAPI boilerplate with best practices",
    version=settings.app_version,
    lifespan=lifespan,
)


# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint redirect info.

    Returns:
        dict: Information about the API
    """
    return {
        "message": "Hello World API",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(health_router.router)
app.include_router(items_router.router)

# Register domain-specific exception handlers
app.add_exception_handler(item_exceptions.ItemNotFoundError, items_router.item_not_found_handler)
app.add_exception_handler(item_exceptions.ItemValidationError, items_router.item_validation_error_handler)
app.add_exception_handler(item_exceptions.ItemAlreadyExistsError, items_router.item_already_exists_handler)


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "hello_world.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
        log_level="info",
    )
