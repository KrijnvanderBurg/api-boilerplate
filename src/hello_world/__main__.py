"""Entry point for the application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from hello_world.exceptions import HelloWorldError
from hello_world.routers import health, items
from hello_world.settings import get_settings
from hello_world.utils.logger import get_logger, set_logger

# Configuration constants
API_PREFIX = "/api/v1"
CORS_ORIGINS: list[str] = []  # Add allowed origins here, e.g., ["http://localhost:3000"]

# Get settings
settings = get_settings()

# Configure logger
set_logger(level=settings.log_level or "INFO")
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
    logger.info(
        "Application starting up",
        version=app.version,
        environment=settings.environment or "unknown",
        debug=settings.debug,
    )
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title="Hello World API",
    description="A production-ready FastAPI boilerplate with best practices",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS enabled", origins=CORS_ORIGINS)


# Exception handlers
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


# Include routers with API prefix
app.include_router(health.router, prefix=API_PREFIX, tags=["health"])
app.include_router(items.router, prefix=API_PREFIX, tags=["items"])


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Root endpoint redirect info.

    Returns:
        dict: Information about the API
    """
    return {
        "message": "Hello World API",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "hello_world.__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower() if settings.log_level else "info",
    )
