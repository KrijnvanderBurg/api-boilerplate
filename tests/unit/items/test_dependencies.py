"""Unit tests for items dependencies."""

import pytest

from hello_world.items import exceptions, schemas
from hello_world.items.dependencies import item_service, valid_item_id
from hello_world.items.models import Item
from hello_world.items.service import ItemService


class TestItemServiceDependency:
    """Test item_service dependency."""

    @pytest.mark.asyncio
    async def test_item_service__creates_item_service_instance(
        self,
        db_session,
    ) -> None:
        """Test that item_service returns ItemService instance."""
        # Act
        result = await item_service(db=db_session)

        # Assert
        assert isinstance(result, ItemService)
        assert result.db is db_session


class TestValidItemIdDependency:
    """Test valid_item_id dependency."""

    @pytest.mark.asyncio
    async def test_valid_item_id__when_item_exists__returns_item(
        self,
        db_session,
    ) -> None:
        """Test that valid_item_id returns item when it exists."""
        # Arrange
        item_id = "existing-item-id"
        service = ItemService(db=db_session)

        # Create test item
        item = Item(id=item_id, name="Test Item", description="Test Description", price=19.99)
        db_session.add(item)
        await db_session.commit()

        # Act
        result = await valid_item_id(item_id=item_id, service=service)

        # Assert
        assert isinstance(result, schemas.ItemResponse)
        assert result.id == item_id
        assert result.name == "Test Item"

    @pytest.mark.asyncio
    async def test_valid_item_id__when_item_not_found__raises_item_not_found_error(
        self,
        db_session,
    ) -> None:
        """Test that valid_item_id raises ItemNotFoundError when item doesn't exist."""
        # Arrange
        item_id = "nonexistent-item-id"
        service = ItemService(db=db_session)

        # Assert
        with pytest.raises(exceptions.ItemNotFoundError):
            # Act
            await valid_item_id(item_id=item_id, service=service)
