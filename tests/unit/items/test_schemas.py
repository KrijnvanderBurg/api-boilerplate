"""Unit tests for items schemas."""

import pytest
from pydantic import ValidationError

from hello_world.items.schemas import ItemCreate, validate_name_not_empty


class TestValidateNameNotEmpty:
    """Test validate_name_not_empty validator."""

    def test_validate_name_not_empty__with_empty_string__raises_value_error(self) -> None:
        """Test that validator raises ValueError for empty string."""
        # Assert
        with pytest.raises(ValueError):
            # Act
            validate_name_not_empty("   ")

    def test_validate_name_not_empty__with_valid_name__returns_stripped_name(self) -> None:
        """Test that validator returns stripped name for valid input."""
        # Act
        result = validate_name_not_empty("  valid name  ")

        # Assert
        assert result == "valid name"


class TestItemCreate:
    """Test ItemCreate schema."""

    def test_item_create__with_empty_name__raises_validation_error(self) -> None:
        """Test that ItemCreate raises ValidationError for empty name."""
        # Assert
        with pytest.raises(ValidationError):
            # Act
            ItemCreate(name="   ", price=10.0)
