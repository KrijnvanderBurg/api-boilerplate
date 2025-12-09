"""Health check endpoints."""

from fastapi import APIRouter, status

from hello_world.settings import get_settings

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is up and running.",
    responses={
        200: {"description": "API is healthy"},
    },
)
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.environment or "unknown",
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the API is ready to accept requests.",
    responses={
        200: {"description": "API is ready"},
    },
)
def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    return {"status": "ready"}
