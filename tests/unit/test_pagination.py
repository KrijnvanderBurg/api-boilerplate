"""Unit tests for pagination utilities."""

import pytest
from pydantic import ValidationError

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

    def test_minimum_limit__accepts_value_1(self) -> None:
        """Test that limit=1 is valid (minimum boundary)."""
        # Act
        params = PaginationParams(limit=1, offset=0)

        # Assert
        assert params.limit == 1

    def test_maximum_limit__accepts_value_100(self) -> None:
        """Test that limit=100 is valid (maximum boundary)."""
        # Act
        params = PaginationParams(limit=100, offset=0)

        # Assert
        assert params.limit == 100

    def test_limit_below_minimum__raises_validation_error(self) -> None:
        """Test that limit=0 raises ValidationError."""
        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            PaginationParams(limit=0, offset=0)

        # Assert error details
        assert "limit" in str(exc_info.value)

    def test_limit_above_maximum__raises_validation_error(self) -> None:
        """Test that limit=101 raises ValidationError."""
        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            PaginationParams(limit=101, offset=0)

        # Assert error details
        assert "limit" in str(exc_info.value)

    def test_negative_offset__raises_validation_error(self) -> None:
        """Test that negative offset raises ValidationError."""
        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            PaginationParams(limit=10, offset=-1)

        # Assert error details
        assert "offset" in str(exc_info.value)

    def test_large_offset__accepts_large_values(self) -> None:
        """Test that large offset values are accepted."""
        # Act
        params = PaginationParams(limit=10, offset=1000000)

        # Assert
        assert params.offset == 1000000


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

    def test_has_more__at_exact_boundary__returns_false(self) -> None:
        """Test that has_more returns False when exactly at the end."""
        # Arrange - offset + limit equals total
        response = PaginatedResponse(items=["a", "b"], total=10, limit=5, offset=5)

        # Assert
        assert response.has_more is False

    def test_has_more__one_before_boundary__returns_true(self) -> None:
        """Test that has_more returns True when one item away from end."""
        # Arrange - offset + limit = total - 1
        response = PaginatedResponse(items=["a", "b"], total=10, limit=5, offset=4)

        # Assert
        assert response.has_more is True

    def test_has_more__with_single_item_limit__calculates_correctly(self) -> None:
        """Test has_more with limit=1."""
        # Arrange
        response = PaginatedResponse(items=["a"], total=5, limit=1, offset=2)

        # Assert
        assert response.has_more is True

    def test_has_more__with_empty_items_but_total_exists__returns_correctly(self) -> None:
        """Test has_more when items list is empty but total indicates more exist."""
        # Arrange - could happen if offset is beyond data
        response = PaginatedResponse(items=[], total=10, limit=5, offset=15)

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

    def test_paginate__with_empty_items__creates_response(self) -> None:
        """Test that paginate works with empty items list."""
        # Act
        result = paginate(items=[], total=0, limit=10, offset=0)

        # Assert
        assert result.items == []
        assert result.total == 0
        assert result.has_more is False

    def test_paginate__with_single_item__creates_response(self) -> None:
        """Test that paginate works with a single item."""
        # Arrange
        items = ["single"]

        # Act
        result = paginate(items=items, total=1, limit=10, offset=0)

        # Assert
        assert result.items == ["single"]
        assert result.total == 1
        assert result.has_more is False

    def test_paginate__preserves_item_order(self) -> None:
        """Test that paginate preserves the order of items."""
        # Arrange
        items = ["z", "y", "x", "w", "v"]

        # Act
        result = paginate(items=items, total=5, limit=5, offset=0)

        # Assert
        assert result.items == ["z", "y", "x", "w", "v"]
