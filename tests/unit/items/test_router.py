"""Unit tests for items router."""

import pytest
from fastapi import Request

from hello_world.items import exceptions, router, schemas
from hello_world.items.models import Item
from hello_world.items.service import ItemService
from hello_world.pagination import PaginationParams


class TestExceptionHandlers:
    """Test exception handler functions."""

    @pytest.mark.asyncio
    async def test_item_not_found_handler__returns_404_response(self) -> None:
        """Test that item_not_found_handler returns 404 with error details."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/items/test-id",
                "headers": [],
                "query_string": b"",
                "server": ("testserver", 80),
            }
        )
        exc = exceptions.ItemNotFoundError("test-id")

        # Act
        response = await router.item_not_found_handler(request, exc)

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_item_validation_error_handler__returns_422_response(self) -> None:
        """Test that item_validation_error_handler returns 422 with validation error."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "path": "/items",
                "headers": [],
                "query_string": b"",
                "server": ("testserver", 80),
            }
        )
        exc = exceptions.ItemValidationError("Invalid price")

        # Act
        response = await router.item_validation_error_handler(request, exc)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_item_already_exists_handler__returns_409_response(self) -> None:
        """Test that item_already_exists_handler returns 409 with conflict error."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "path": "/items",
                "headers": [],
                "query_string": b"",
                "server": ("testserver", 80),
            }
        )
        exc = exceptions.ItemAlreadyExistsError("Duplicate")

        # Act
        response = await router.item_already_exists_handler(request, exc)

        # Assert
        assert response.status_code == 409


class TestCreateItemEndpoint:
    """Test create_item endpoint."""

    @pytest.mark.asyncio
    async def test_create_item__with_valid_data__returns_created_item(
        self,
        db_session,
    ) -> None:
        """Test that create_item endpoint creates and returns item."""
        # Arrange
        item_create = schemas.ItemCreate(name="New Item", description="Description", price=29.99)
        service = ItemService(db=db_session)

        # Act
        result = await router.create_item(item=item_create, service=service)

        # Assert
        assert isinstance(result, schemas.ItemResponse)
        assert result.name == "New Item"
        assert result.description == "Description"
        assert result.price == 29.99


class TestReadItemsEndpoint:
    """Test read_items endpoint."""

    @pytest.mark.asyncio
    async def test_read_items__returns_paginated_response(
        self,
        db_session,
    ) -> None:
        """Test that read_items endpoint returns paginated items."""
        # Arrange
        service = ItemService(db=db_session)

        # Create test items
        item1 = Item(id="1", name="Item 1", description="Desc 1", price=10.0)
        item2 = Item(id="2", name="Item 2", description="Desc 2", price=20.0)
        db_session.add_all([item1, item2])
        await db_session.commit()

        pagination = PaginationParams(limit=10, offset=0)

        # Act
        result = await router.read_items(pagination=pagination, service=service)

        # Assert
        assert len(result.items) == 2
        assert result.total == 2
        assert result.limit == 10
        assert result.offset == 0


class TestReadItemEndpoint:
    """Test read_item endpoint."""

    @pytest.mark.asyncio
    async def test_read_item__returns_item(self) -> None:
        """Test that read_item endpoint returns the validated item."""
        # Arrange
        item = schemas.ItemResponse(
            id="test-id",
            name="Test Item",
            description="Test Description",
            price=19.99,
        )

        # Act - validation happens in dependency
        result = await router.read_item(item=item)

        # Assert
        assert result == item


class TestUpdateItemEndpoint:
    """Test update_item endpoint."""

    @pytest.mark.asyncio
    async def test_update_item__with_valid_data__returns_updated_item(
        self,
        db_session,
    ) -> None:
        """Test that update_item endpoint updates and returns item."""
        # Arrange
        service = ItemService(db=db_session)

        # Create existing item
        existing_item_model = Item(id="update-id", name="Old Name", description="Old Desc", price=10.0)
        db_session.add(existing_item_model)
        await db_session.commit()

        existing_item = schemas.ItemResponse(
            id="update-id",
            name="Old Name",
            description="Old Desc",
            price=10.0,
        )
        item_update = schemas.ItemUpdate(name="New Name", description="New Desc", price=25.0)

        # Act
        result = await router.update_item(item_update=item_update, item=existing_item, service=service)

        # Assert
        assert result.id == "update-id"
        assert result.name == "New Name"
        assert result.description == "New Desc"
        assert result.price == 25.0

    @pytest.mark.asyncio
    async def test_update_item__when_service_returns_none__raises_item_not_found_error(
        self,
        db_session,
    ) -> None:
        """Test that update_item raises ItemNotFoundError when service returns None."""
        # Arrange
        service = ItemService(db=db_session)

        existing_item = schemas.ItemResponse(
            id="nonexistent-id",
            name="Old Name",
            description="Old Desc",
            price=10.0,
        )
        item_update = schemas.ItemUpdate(name="New Name", description="New Desc", price=25.0)

        # Assert
        with pytest.raises(exceptions.ItemNotFoundError):
            # Act
            await router.update_item(item_update=item_update, item=existing_item, service=service)


class TestDeleteItemEndpoint:
    """Test delete_item endpoint."""

    @pytest.mark.asyncio
    async def test_delete_item__deletes_item(
        self,
        db_session,
    ) -> None:
        """Test that delete_item endpoint deletes the validated item."""
        # Arrange
        service = ItemService(db=db_session)

        # Create item to delete
        item_model = Item(id="delete-id", name="To Delete", description="Description", price=10.0)
        db_session.add(item_model)
        await db_session.commit()

        item = schemas.ItemResponse(
            id="delete-id",
            name="To Delete",
            description="Description",
            price=10.0,
        )

        # Act
        result = await router.delete_item(item=item, service=service)

        # Assert
        assert result is None
