"""Unit tests for ItemService class."""

from uuid import UUID

import pytest
from sqlalchemy import select

from hello_world.items import schemas
from hello_world.items.exceptions import ItemAlreadyExistsError
from hello_world.items.models import Item
from hello_world.items.service import ItemService


class TestItemServiceCreateItem:
    """Test ItemService.create_item method."""

    @pytest.mark.asyncio
    async def test_create_item__with_valid_data__returns_item_response(
        self,
        db_session,
    ) -> None:
        """Test that create_item successfully creates and returns an item."""
        # Arrange
        service = ItemService(db=db_session)
        item_create = schemas.ItemCreate(name="Test Item", description="Test Description", price=19.99)

        # Act
        result = await service.create_item(item_create)

        # Assert
        assert isinstance(result, schemas.ItemResponse)
        assert result.name == "Test Item"
        assert result.description == "Test Description"
        assert result.price == 19.99
        # Validate UUID format
        UUID(result.id)

        # Verify item exists in database
        db_result = await db_session.execute(select(Item).where(Item.name == "Test Item"))
        db_item = db_result.scalar_one_or_none()
        assert db_item is not None
        assert db_item.id == result.id

    @pytest.mark.asyncio
    async def test_create_item__with_duplicate_name__raises_item_already_exists_error(
        self,
        db_session,
    ) -> None:
        """Test that create_item raises ItemAlreadyExistsError for duplicate names."""
        # Arrange
        service = ItemService(db=db_session)
        item_create = schemas.ItemCreate(name="Duplicate Item", description="Description", price=29.99)

        # Create first item
        await service.create_item(item_create)

        # Assert - try to create duplicate
        with pytest.raises(ItemAlreadyExistsError):
            # Act
            await service.create_item(item_create)

    @pytest.mark.asyncio
    async def test_create_item__without_description__creates_item_successfully(
        self,
        db_session,
    ) -> None:
        """Test that create_item works when description is None."""
        # Arrange
        service = ItemService(db=db_session)
        item_create = schemas.ItemCreate(name="No Desc", description=None, price=9.99)

        # Act
        result = await service.create_item(item_create)

        # Assert
        assert result.name == "No Desc"
        assert result.description is None
        assert result.price == 9.99


class TestItemServiceReadItems:
    """Test ItemService.read_items method."""

    @pytest.mark.asyncio
    async def test_read_items__with_items_in_database__returns_items_and_count(
        self,
        db_session,
    ) -> None:
        """Test that read_items returns paginated items and total count."""
        # Arrange
        service = ItemService(db=db_session)

        # Create test items
        item1 = Item(id="id1", name="Item 1", description="Desc 1", price=10.0)
        item2 = Item(id="id2", name="Item 2", description="Desc 2", price=20.0)
        item3 = Item(id="id3", name="Item 3", description="Desc 3", price=30.0)
        db_session.add_all([item1, item2, item3])
        await db_session.commit()

        # Act
        items, total = await service.read_items(limit=2, offset=0)

        # Assert
        assert len(items) == 2
        assert total == 3
        assert items[0].name in ["Item 1", "Item 2", "Item 3"]
        assert items[1].name in ["Item 1", "Item 2", "Item 3"]

    @pytest.mark.asyncio
    async def test_read_items__with_empty_database__returns_empty_list(
        self,
        db_session,
    ) -> None:
        """Test that read_items returns empty list when no items exist."""
        # Arrange
        service = ItemService(db=db_session)

        # Act
        items, total = await service.read_items(limit=10, offset=0)

        # Assert
        assert items == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_read_items__with_custom_pagination__respects_limit_and_offset(
        self,
        db_session,
    ) -> None:
        """Test that read_items uses custom limit and offset parameters."""
        # Arrange
        service = ItemService(db=db_session)

        # Create 5 test items
        for i in range(5):
            item = Item(id=f"id{i}", name=f"Item {i}", description=f"Desc {i}", price=10.0 * i)
            db_session.add(item)
        await db_session.commit()

        # Act
        items, total = await service.read_items(limit=2, offset=2)

        # Assert
        assert len(items) == 2
        assert total == 5


class TestItemServiceReadItem:
    """Test ItemService.read_item method."""

    @pytest.mark.asyncio
    async def test_read_item__when_item_exists__returns_item_response(
        self,
        db_session,
    ) -> None:
        """Test that read_item returns item when it exists."""
        # Arrange
        service = ItemService(db=db_session)
        item_id = "test-id-123"

        # Create test item
        item = Item(id=item_id, name="Found Item", description="Found Desc", price=15.0)
        db_session.add(item)
        await db_session.commit()

        # Act
        result = await service.read_item(item_id)

        # Assert
        assert result is not None
        assert result.id == item_id
        assert result.name == "Found Item"
        assert result.description == "Found Desc"
        assert result.price == 15.0

    @pytest.mark.asyncio
    async def test_read_item__when_item_not_found__returns_none(
        self,
        db_session,
    ) -> None:
        """Test that read_item returns None when item doesn't exist."""
        # Arrange
        service = ItemService(db=db_session)
        item_id = "nonexistent-id"

        # Act
        result = await service.read_item(item_id)

        # Assert
        assert result is None


class TestItemServiceUpdateItem:
    """Test ItemService.update_item method."""

    @pytest.mark.asyncio
    async def test_update_item__with_valid_data__updates_and_returns_item(
        self,
        db_session,
    ) -> None:
        """Test that update_item successfully updates and returns the item."""
        # Arrange
        service = ItemService(db=db_session)
        item_id = "update-id"

        # Create test item
        item = Item(id=item_id, name="Old Name", description="Old Desc", price=10.0)
        db_session.add(item)
        await db_session.commit()

        item_update = schemas.ItemUpdate(name="New Name", description="New Desc", price=25.0)

        # Act
        result = await service.update_item(item_id, item_update)

        # Assert
        assert result is not None
        assert result.name == "New Name"
        assert result.description == "New Desc"
        assert result.price == 25.0

        # Verify in database
        db_result = await db_session.execute(select(Item).where(Item.id == item_id))
        db_item = db_result.scalar_one_or_none()
        assert db_item is not None
        assert db_item.name == "New Name"

    @pytest.mark.asyncio
    async def test_update_item__when_item_not_found__returns_none(
        self,
        db_session,
    ) -> None:
        """Test that update_item returns None when item doesn't exist."""
        # Arrange
        service = ItemService(db=db_session)
        item_id = "nonexistent-id"
        item_update = schemas.ItemUpdate(name="Name", description="Desc", price=10.0)

        # Act
        result = await service.update_item(item_id, item_update)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_item__with_duplicate_name__raises_item_already_exists_error(
        self,
        db_session,
    ) -> None:
        """Test that update_item raises ItemAlreadyExistsError for duplicate names."""
        # Arrange
        service = ItemService(db=db_session)

        # Create two items
        item1 = Item(id="id1", name="Original", description="Desc", price=10.0)
        item2 = Item(id="id2", name="Existing", description="Desc", price=20.0)
        db_session.add_all([item1, item2])
        await db_session.commit()

        # Try to update item1 with item2's name
        item_update = schemas.ItemUpdate(name="Existing", description="Desc", price=10.0)

        # Assert
        with pytest.raises(ItemAlreadyExistsError):
            # Act
            await service.update_item("id1", item_update)


class TestItemServiceDeleteItem:
    """Test ItemService.delete_item method."""

    @pytest.mark.asyncio
    async def test_delete_item__when_item_exists__deletes_and_returns_true(
        self,
        db_session,
    ) -> None:
        """Test that delete_item successfully deletes item and returns True."""
        # Arrange
        service = ItemService(db=db_session)
        item_id = "delete-id"

        # Create test item
        item = Item(id=item_id, name="To Delete", description="Desc", price=10.0)
        db_session.add(item)
        await db_session.commit()

        # Act
        result = await service.delete_item(item_id)

        # Assert
        assert result is True

        # Verify item is deleted
        db_result = await db_session.execute(select(Item).where(Item.id == item_id))
        db_item = db_result.scalar_one_or_none()
        assert db_item is None

    @pytest.mark.asyncio
    async def test_delete_item__when_item_not_found__returns_false(
        self,
        db_session,
    ) -> None:
        """Test that delete_item returns False when item doesn't exist."""
        # Arrange
        service = ItemService(db=db_session)
        item_id = "nonexistent-id"

        # Act
        result = await service.delete_item(item_id)

        # Assert
        assert result is False
