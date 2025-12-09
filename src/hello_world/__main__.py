"""Entry point for the application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from hello_world.exceptions import HelloWorldError, ItemAlreadyExistsError, ItemNotFoundError, ItemValidationError
from hello_world.routers import health, items
from hello_world.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application lifespan events.

    This context manager handles startup and shutdown events for the application.
    Use this to initialize resources on startup and clean them up on shutdown.

    Args:
        app: The FastAPI application instance

    Yields:
        None: Control during the application's lifetime
    """
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Hello World API",
    description="A production-ready FastAPI boilerplate with best practices",
    version="0.1.0",
    lifespan=lifespan,
)


# Exception handlers
@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    """Handle ItemNotFoundError exceptions.

    Args:
        request: The incoming request
        exc: The ItemNotFoundError exception

    Returns:
        JSONResponse: Error response with 404 status
    """
    logger.warning(
        "Item not found",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "type": "ItemNotFoundError",
        },
    )


@app.exception_handler(ItemValidationError)
async def item_validation_error_handler(request: Request, exc: ItemValidationError) -> JSONResponse:
    """Handle ItemValidationError exceptions.

    Args:
        request: The incoming request
        exc: The ItemValidationError exception

    Returns:
        JSONResponse: Error response with 422 status
    """
    logger.warning(
        "Item validation error",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "type": "ItemValidationError",
        },
    )


@app.exception_handler(ItemAlreadyExistsError)
async def item_already_exists_handler(request: Request, exc: ItemAlreadyExistsError) -> JSONResponse:
    """Handle ItemAlreadyExistsError exceptions.

    Args:
        request: The incoming request
        exc: The ItemAlreadyExistsError exception

    Returns:
        JSONResponse: Error response with 409 status
    """
    logger.warning(
        "Item already exists",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": str(exc),
            "type": "ItemAlreadyExistsError",
        },
    )


@app.exception_handler(HelloWorldError)
async def hello_world_error_handler(request: Request, exc: HelloWorldError) -> JSONResponse:
    """Handle custom HelloWorld exceptions.

    Args:
        request: The incoming request
        exc: The HelloWorldError exception

    Returns:
        JSONResponse: Error response with details and exit code
    """
    logger.error(
        "HelloWorld error occurred",
        error=str(exc),
        exit_code=exc.exit_code,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "exit_code": exc.exit_code,
            "type": "HelloWorldError",
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle validation ValueError exceptions.

    Args:
        request: The incoming request
        exc: The ValueError exception

    Returns:
        JSONResponse: Error response with validation details
    """
    logger.warning(
        "Validation error occurred",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "type": "ValueError",
        },
    )


# Root endpoint
@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
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
app.include_router(health.router, tags=["health"])
app.include_router(items.router, tags=["items"])


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "hello_world.__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
