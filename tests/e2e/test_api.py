"""End-to-end tests for the API."""

import pytest
from fastapi.testclient import TestClient

from hello_world.__main__ import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the API.

    Returns:
        TestClient: A test client for making requests to the API
    """
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data

    def test_readiness_check(self, client: TestClient) -> None:
        """Test the readiness check endpoint."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "health" in data


class TestItemsEndpoints:
    """Tests for items CRUD endpoints."""

    def test_create_item_success(self, client: TestClient) -> None:
        """Test creating a new item successfully."""
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99,
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] == item_data["description"]
        assert data["price"] == item_data["price"]
        assert "id" in data

    def test_create_item_without_description(self, client: TestClient) -> None:
        """Test creating an item without optional description."""
        item_data = {
            "name": "Minimal Item",
            "price": 9.99,
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] is None
        assert data["price"] == item_data["price"]

    def test_create_item_invalid_price(self, client: TestClient) -> None:
        """Test creating an item with invalid price."""
        item_data = {
            "name": "Invalid Item",
            "price": -10.00,
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 422

    def test_create_item_empty_name(self, client: TestClient) -> None:
        """Test creating an item with empty name."""
        item_data = {
            "name": "   ",
            "price": 10.00,
        }
        response = client.post("/items", json=item_data)
        assert response.status_code == 422

    def test_create_item_missing_required_fields(self, client: TestClient) -> None:
        """Test creating an item without required fields."""
        item_data = {"name": "Incomplete Item"}
        response = client.post("/items", json=item_data)
        assert response.status_code == 422

    def test_list_items_empty(self, client: TestClient) -> None:
        """Test listing items when none exist."""
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_items_with_data(self, client: TestClient) -> None:
        """Test listing items after creating some."""
        # Create items
        items_to_create = [
            {"name": "Item 1", "price": 10.00},
            {"name": "Item 2", "price": 20.00},
            {"name": "Item 3", "price": 30.00},
        ]
        for item_data in items_to_create:
            client.post("/items", json=item_data)

        # List items
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(items_to_create)

    def test_get_item_by_id(self, client: TestClient) -> None:
        """Test retrieving a specific item by ID."""
        # Create an item
        item_data = {"name": "Specific Item", "price": 15.99}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Get the item
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == item_data["name"]
        assert data["price"] == item_data["price"]

    def test_get_item_not_found(self, client: TestClient) -> None:
        """Test retrieving a non-existent item."""
        response = client.get("/items/nonexistent-id")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_update_item_success(self, client: TestClient) -> None:
        """Test updating an item successfully."""
        # Create an item
        item_data = {"name": "Original Name", "price": 25.00}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Update the item
        update_data = {"name": "Updated Name", "price": 30.00}
        response = client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == update_data["name"]
        assert data["price"] == update_data["price"]

    def test_update_item_partial(self, client: TestClient) -> None:
        """Test partial update of an item."""
        # Create an item
        item_data = {"name": "Original", "description": "Original description", "price": 20.00}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Partial update (only name)
        update_data = {"name": "Updated Name Only"}
        response = client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == item_data["description"]  # Unchanged
        assert data["price"] == item_data["price"]  # Unchanged

    def test_update_item_not_found(self, client: TestClient) -> None:
        """Test updating a non-existent item."""
        update_data = {"name": "Updated", "price": 50.00}
        response = client.put("/items/nonexistent-id", json=update_data)
        assert response.status_code == 404

    def test_update_item_invalid_data(self, client: TestClient) -> None:
        """Test updating an item with invalid data."""
        # Create an item
        item_data = {"name": "Test Item", "price": 10.00}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Try to update with invalid price
        update_data = {"price": -5.00}
        response = client.put(f"/items/{item_id}", json=update_data)
        assert response.status_code == 422

    def test_delete_item_success(self, client: TestClient) -> None:
        """Test deleting an item successfully."""
        # Create an item
        item_data = {"name": "To Be Deleted", "price": 5.00}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Delete the item
        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, client: TestClient) -> None:
        """Test deleting a non-existent item."""
        response = client.delete("/items/nonexistent-id")
        assert response.status_code == 404


class TestItemsCRUDFlow:
    """Integration tests for complete CRUD flow."""

    def test_full_crud_flow(self, client: TestClient) -> None:
        """Test a complete CRUD flow: Create, Read, Update, Delete."""
        # Create
        create_data = {
            "name": "Flow Test Item",
            "description": "Testing full CRUD flow",
            "price": 99.99,
        }
        create_response = client.post("/items", json=create_data)
        assert create_response.status_code == 201
        item = create_response.json()
        item_id = item["id"]

        # Read
        read_response = client.get(f"/items/{item_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == create_data["name"]

        # Update
        update_data = {"name": "Updated Flow Test", "price": 149.99}
        update_response = client.put(f"/items/{item_id}", json=update_data)
        assert update_response.status_code == 200
        updated_item = update_response.json()
        assert updated_item["name"] == update_data["name"]
        assert updated_item["price"] == update_data["price"]

        # Delete
        delete_response = client.delete(f"/items/{item_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        final_read = client.get(f"/items/{item_id}")
        assert final_read.status_code == 404
