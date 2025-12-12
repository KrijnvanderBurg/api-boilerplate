"""End-to-end tests for the API.

Following FastAPI best practices, all integration tests use async test client
with httpx to avoid event loop issues and properly test async endpoints.
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient) -> None:
        """Test the health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data

    @pytest.mark.asyncio
    async def test_readiness_check(self, client: AsyncClient) -> None:
        """Test the readiness check endpoint."""
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient) -> None:
        """Test the root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "health" in data["endpoints"]
        assert "items" in data["endpoints"]


class TestItemsEndpoints:
    """Tests for items CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_item_success(self, client: AsyncClient) -> None:
        """Test creating a new item successfully."""
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99,
        }
        response = await client.post("/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] == item_data["description"]
        assert data["price"] == item_data["price"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_item_without_description(self, client: AsyncClient) -> None:
        """Test creating an item without optional description."""
        item_data = {
            "name": "Minimal Item",
            "price": 9.99,
        }
        response = await client.post("/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] is None
        assert data["price"] == item_data["price"]

    @pytest.mark.asyncio
    async def test_create_item_invalid_price(self, client: AsyncClient) -> None:
        """Test creating an item with invalid price."""
        item_data = {
            "name": "Invalid Item",
            "price": -10.00,
        }
        response = await client.post("/items", json=item_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_item_empty_name(self, client: AsyncClient) -> None:
        """Test creating an item with empty name."""
        item_data = {
            "name": "   ",
            "price": 10.00,
        }
        response = await client.post("/items", json=item_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_item_duplicate_name(self, client: AsyncClient) -> None:
        """Test creating an item with duplicate name returns 409."""
        item_data = {
            "name": "Duplicate Test Item",
            "price": 10.00,
        }
        # Create first item
        response1 = await client.post("/items", json=item_data)
        assert response1.status_code == 201

        # Try to create second item with same name
        response2 = await client.post("/items", json=item_data)
        assert response2.status_code == 409
        data = response2.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_item_missing_required_fields(self, client: AsyncClient) -> None:
        """Test creating an item without required fields."""
        item_data = {"name": "Incomplete Item"}
        response = await client.post("/items", json=item_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_read_items_empty(self, client: AsyncClient) -> None:
        """Test listing items when none exist."""
        response = await client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_read_items_with_data(self, client: AsyncClient) -> None:
        """Test listing items after creating some."""
        # Create items
        items_to_create = [
            {"name": "Item 1", "price": 10.00},
            {"name": "Item 2", "price": 20.00},
            {"name": "Item 3", "price": 30.00},
        ]
        for item_data in items_to_create:
            await client.post("/items", json=item_data)

        # List items
        response = await client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) >= len(items_to_create)

    @pytest.mark.asyncio
    async def test_read_item_by_id(self, client: AsyncClient) -> None:
        """Test retrieving a specific item by ID."""
        # Create an item
        item_data = {"name": "Specific Item", "price": 15.99}
        create_response = await client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Get the item
        response = await client.get(f"/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == item_data["name"]
        assert data["price"] == item_data["price"]

    @pytest.mark.asyncio
    async def test_read_item_not_found(self, client: AsyncClient) -> None:
        """Test retrieving a non-existent item."""
        response = await client.get("/items/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_update_item_success(self, client: AsyncClient) -> None:
        """Test updating an item successfully."""
        # Create an item
        item_data = {"name": "Original", "description": "Original description", "price": 20.00}
        create_response = await client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Update the item
        update_data = {"name": "Updated Name", "description": "Updated description", "price": 25.00}
        response = await client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["price"] == update_data["price"]

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, client: AsyncClient) -> None:
        """Test updating a non-existent item."""
        update_data = {"name": "Updated", "price": 50.00}
        response = await client.put("/items/nonexistent-id", json=update_data)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_item_invalid_data(self, client: AsyncClient) -> None:
        """Test updating an item with invalid data."""
        # Create an item
        item_data = {"name": "Update Invalid Test Item", "price": 10.00}
        create_response = await client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Try to update with invalid price
        update_data = {"name": "Update Invalid Test Item", "price": -5.00}
        response = await client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_item_duplicate_name(self, client: AsyncClient) -> None:
        """Test updating an item to a duplicate name returns 409."""
        # Create two items
        item1_data = {"name": "Update Item 1", "price": 10.00}
        item2_data = {"name": "Update Item 2", "price": 20.00}

        response1 = await client.post("/items", json=item1_data)
        response2 = await client.post("/items", json=item2_data)

        item1_id = response1.json()["id"]

        # Try to update item1 to have the same name as item2
        update_data = {"name": "Update Item 2", "price": 15.00}
        response = await client.put(f"/items/{item1_id}", json=update_data)
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_item_success(self, client: AsyncClient) -> None:
        """Test deleting an item successfully."""
        # Create an item
        item_data = {"name": "To Be Deleted", "price": 5.00}
        create_response = await client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Delete the item
        response = await client.delete(f"/items/{item_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, client: AsyncClient) -> None:
        """Test deleting a non-existent item."""
        response = await client.delete("/items/nonexistent-id")
        assert response.status_code == 404


class TestItemsCRUDFlow:
    """Integration tests for complete CRUD flow."""

    @pytest.mark.asyncio
    async def test_full_crud_flow(self, client: AsyncClient) -> None:
        """Test a complete CRUD flow: Create, Read, Update, Delete."""
        # Create
        create_data = {
            "name": "Flow Test Item",
            "description": "Testing full CRUD flow",
            "price": 99.99,
        }
        create_response = await client.post("/items", json=create_data)
        assert create_response.status_code == 201
        item = create_response.json()
        item_id = item["id"]

        # Read
        read_response = await client.get(f"/items/{item_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == create_data["name"]

        # Update
        update_data = {"name": "Updated Flow Test", "price": 149.99}
        update_response = await client.put(f"/items/{item_id}", json=update_data)
        assert update_response.status_code == 200
        updated_item = update_response.json()
        assert updated_item["name"] == update_data["name"]
        assert updated_item["price"] == update_data["price"]

        # Delete
        delete_response = await client.delete(f"/items/{item_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        final_read = await client.get(f"/items/{item_id}")
        assert final_read.status_code == 404
