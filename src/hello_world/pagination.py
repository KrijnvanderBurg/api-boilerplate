"""Pagination utilities for list endpoints."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    limit: int = Field(default=10, ge=1, le=100, description="Max items to return")
    offset: int = Field(default=0, ge=0, description="Items to skip")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int
    limit: int
    offset: int

    @computed_field
    def has_more(self) -> bool:
        """Check if more items available."""
        return (self.offset + self.limit) < self.total


def paginate(items: list[T], total: int, limit: int, offset: int) -> PaginatedResponse[T]:
    """Create a paginated response.

    Args:
        items: List of items for the current page
        total: Total number of items available
        limit: Maximum number of items per page
        offset: Current offset

    Returns:
        PaginatedResponse: Paginated response with metadata
    """
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
