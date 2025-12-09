"""Pagination utilities for list endpoints.

This module provides standardized pagination functionality following FastAPI
best practices. Use these utilities to ensure consistent pagination across
all list endpoints.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints.

    Attributes:
        limit: Maximum number of items to return
        offset: Number of items to skip
    """

    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of items to return")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Attributes:
        items: List of items in the current page
        total: Total number of items available
        limit: Maximum number of items per page
        offset: Current offset
        has_more: Whether there are more items available
    """

    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Check if there are more items available.

        Returns:
            bool: True if there are more items beyond the current page
        """
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
