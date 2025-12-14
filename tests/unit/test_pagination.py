"""Unit tests for pagination utilities."""

from hello_world.pagination import PaginatedResponse, PaginationParams, paginate


class TestPaginationParams:
    """Test PaginationParams model."""

    def test_default_values__creates_with_defaults(self) -> None:
        """Test that PaginationParams has correct default values."""
        # Act
        params = PaginationParams()

        # Assert
        assert params.limit == 10
        assert params.offset == 0


class TestPaginatedResponse:
    """Test PaginatedResponse model."""

    def test_has_more__when_more_items_available__returns_true(self) -> None:
        """Test that has_more returns True when more items available."""
        # Arrange
        response = PaginatedResponse(items=["a", "b"], total=20, limit=10, offset=0)

        # Assert
        assert response.has_more is True

    def test_has_more__when_no_more_items__returns_false(self) -> None:
        """Test that has_more returns False when no more items available."""
        # Arrange
        response = PaginatedResponse(items=["a", "b"], total=2, limit=10, offset=0)

        # Assert
        assert response.has_more is False


class TestPaginate:
    """Test paginate function."""

    def test_paginate__creates_paginated_response(self) -> None:
        """Test that paginate creates a PaginatedResponse."""
        # Arrange
        items = ["item1", "item2", "item3"]

        # Act
        result = paginate(items=items, total=10, limit=3, offset=0)

        # Assert
        assert isinstance(result, PaginatedResponse)
        assert result.items == items
        assert result.total == 10
        assert result.limit == 3
        assert result.offset == 0
