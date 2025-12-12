"""Health check endpoints."""

from fastapi import APIRouter, status

from hello_world.logger import get_logger
from hello_world.settings import Settings, get_settings

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is up and running.",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "environment": "development",
                    }
                }
            },
        },
    },
)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    settings: Settings = get_settings()
    response = {
        "status": "healthy",
        "environment": str(settings.environment),
    }
    logger.debug("Health check completed", environment=settings.environment)
    return response


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the API is ready to accept requests.",
    responses={
        200: {
            "description": "API is ready",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ready",
                    }
                }
            },
        },
    },
)
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    logger.debug("Readiness check endpoint accessed")
    return {"status": "ready"}
