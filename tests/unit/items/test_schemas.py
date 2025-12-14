"""Unit tests for items schemas."""

import pytest
from pydantic import ValidationError

from hello_world.items import constants
from hello_world.items.schemas import ItemCreate, ItemResponse, ItemUpdate, validate_name_not_empty


class TestValidateNameNotEmpty:
    """Test validate_name_not_empty validator."""

    def test_validate_name_not_empty__with_empty_string__raises_value_error(self) -> None:
        """Test that validator raises ValueError for empty string."""
        # Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            # Act
            validate_name_not_empty("   ")

    def test_validate_name_not_empty__with_valid_name__returns_stripped_name(self) -> None:
        """Test that validator returns stripped name for valid input."""
        # Act
        result = validate_name_not_empty("  valid name  ")

        # Assert
        assert result == "valid name"

    def test_validate_name_not_empty__with_whitespace_only__raises_value_error(self) -> None:
        """Test that validator raises ValueError for whitespace-only string."""
        # Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            # Act
            validate_name_not_empty("\t\n  ")

    def test_validate_name_not_empty__with_single_space__raises_value_error(self) -> None:
        """Test that validator raises ValueError for single space."""
        # Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            # Act
            validate_name_not_empty(" ")


class TestItemCreate:
    """Test ItemCreate schema."""

    def test_item_create__with_empty_name__raises_validation_error(self) -> None:
        """Test that ItemCreate raises ValidationError for empty name."""
        # Assert
        with pytest.raises(ValidationError):
            # Act
            ItemCreate(name="   ", price=10.0)

    def test_item_create__with_valid_data__creates_successfully(self) -> None:
        """Test that ItemCreate accepts valid data."""
        # Act
        item = ItemCreate(name="Valid Item", description="A description", price=19.99)

        # Assert
        assert item.name == "Valid Item"
        assert item.description == "A description"
        assert item.price == 19.99

    def test_item_create__with_minimum_price__accepts_value(self) -> None:
        """Test that ItemCreate accepts minimum valid price."""
        # Act
        item = ItemCreate(name="Cheap Item", price=constants.ITEM_PRICE_MIN)

        # Assert
        assert item.price == constants.ITEM_PRICE_MIN

    def test_item_create__with_zero_price__raises_validation_error(self) -> None:
        """Test that ItemCreate raises ValidationError for zero price."""
        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            ItemCreate(name="Free Item", price=0.0)

        # Verify error is about price
        assert "price" in str(exc_info.value)

    def test_item_create__with_negative_price__raises_validation_error(self) -> None:
        """Test that ItemCreate raises ValidationError for negative price."""
        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            ItemCreate(name="Negative Item", price=-10.0)

        # Verify error is about price
        assert "price" in str(exc_info.value)

    def test_item_create__with_max_length_name__accepts_value(self) -> None:
        """Test that ItemCreate accepts name at maximum length."""
        # Arrange
        max_name = "A" * constants.ITEM_NAME_MAX_LENGTH

        # Act
        item = ItemCreate(name=max_name, price=10.0)

        # Assert
        assert len(item.name) == constants.ITEM_NAME_MAX_LENGTH

    def test_item_create__with_name_too_long__raises_validation_error(self) -> None:
        """Test that ItemCreate raises ValidationError for name exceeding max length."""
        # Arrange
        too_long_name = "A" * (constants.ITEM_NAME_MAX_LENGTH + 1)

        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            ItemCreate(name=too_long_name, price=10.0)

        # Verify error is about name
        assert "name" in str(exc_info.value)

    def test_item_create__with_max_length_description__accepts_value(self) -> None:
        """Test that ItemCreate accepts description at maximum length."""
        # Arrange
        max_desc = "B" * constants.ITEM_DESCRIPTION_MAX_LENGTH

        # Act
        item = ItemCreate(name="Item", description=max_desc, price=10.0)

        # Assert
        assert len(item.description) == constants.ITEM_DESCRIPTION_MAX_LENGTH

    def test_item_create__with_description_too_long__raises_validation_error(self) -> None:
        """Test that ItemCreate raises ValidationError for description exceeding max length."""
        # Arrange
        too_long_desc = "B" * (constants.ITEM_DESCRIPTION_MAX_LENGTH + 1)

        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            ItemCreate(name="Item", description=too_long_desc, price=10.0)

        # Verify error is about description
        assert "description" in str(exc_info.value)

    def test_item_create__without_description__defaults_to_none(self) -> None:
        """Test that ItemCreate description defaults to None when not provided."""
        # Act
        item = ItemCreate(name="Item", price=10.0)

        # Assert
        assert item.description is None

    def test_item_create__with_none_description__accepts_none(self) -> None:
        """Test that ItemCreate accepts explicit None for description."""
        # Act
        item = ItemCreate(name="Item", description=None, price=10.0)

        # Assert
        assert item.description is None


class TestItemUpdate:
    """Test ItemUpdate schema."""

    def test_item_update__with_valid_data__creates_successfully(self) -> None:
        """Test that ItemUpdate accepts valid data."""
        # Act
        item = ItemUpdate(name="Updated Item", description="Updated", price=29.99)

        # Assert
        assert item.name == "Updated Item"
        assert item.description == "Updated"
        assert item.price == 29.99

    def test_item_update__with_empty_name__raises_validation_error(self) -> None:
        """Test that ItemUpdate raises ValidationError for empty name."""
        # Assert
        with pytest.raises(ValidationError):
            # Act
            ItemUpdate(name="   ", price=10.0)

    def test_item_update__with_zero_price__raises_validation_error(self) -> None:
        """Test that ItemUpdate raises ValidationError for zero price."""
        # Assert
        with pytest.raises(ValidationError) as exc_info:
            # Act
            ItemUpdate(name="Item", price=0.0)

        # Verify error is about price
        assert "price" in str(exc_info.value)

    def test_item_update__has_same_validation_as_create(self) -> None:
        """Test that ItemUpdate has same validation rules as ItemCreate."""
        # Arrange
        max_name = "A" * constants.ITEM_NAME_MAX_LENGTH

        # Act - should accept same values as ItemCreate
        item = ItemUpdate(name=max_name, description="test", price=constants.ITEM_PRICE_MIN)

        # Assert
        assert item.name == max_name
        assert item.price == constants.ITEM_PRICE_MIN


class TestItemResponse:
    """Test ItemResponse schema."""

    def test_item_response__with_all_fields__creates_successfully(self) -> None:
        """Test that ItemResponse accepts all required fields."""
        # Act
        item = ItemResponse(id="test-id", name="Item", description="Desc", price=19.99)

        # Assert
        assert item.id == "test-id"
        assert item.name == "Item"
        assert item.description == "Desc"
        assert item.price == 19.99

    def test_item_response__inherits_from_item_create(self) -> None:
        """Test that ItemResponse inherits validation from ItemCreate."""
        # Assert - should raise same validation errors as ItemCreate
        with pytest.raises(ValidationError):
            # Act
            ItemResponse(id="test-id", name="   ", price=10.0)

    def test_item_response__with_from_attributes__converts_orm_model(self) -> None:
        """Test that ItemResponse can be created from ORM model attributes."""

        # Arrange - simulate an ORM object
        class MockORM:
            id = "orm-id"
            name = "ORM Item"
            description = "ORM Description"
            price = 29.99

        # Act
        item = ItemResponse.model_validate(MockORM())

        # Assert
        assert item.id == "orm-id"
        assert item.name == "ORM Item"
        assert item.description == "ORM Description"
        assert item.price == 29.99
