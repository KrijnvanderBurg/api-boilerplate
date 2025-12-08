"""Items API router."""

from typing import List

from fastapi import APIRouter, HTTPException

from hello_world.api.models.item import Item, ItemCreate, ItemUpdate
from hello_world.api.services.item_service import ItemService

router = APIRouter()
item_service = ItemService()


@router.post("/items", status_code=201)
async def create_item(item: ItemCreate) -> Item:
    """Create a new item."""
    return item_service.create_item(item)


@router.get("/items")
async def list_items() -> List[Item]:
    """List all items."""
    return item_service.list_items()


@router.get("/items/{item_id}")
async def get_item(item_id: str) -> Item:
    """Get an item by ID."""
    item = item_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/items/{item_id}")
async def update_item(item_id: str, item_update: ItemUpdate) -> Item:
    """Update an item."""
    item = item_service.update_item(item_id, item_update)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    """Delete an item."""
    if not item_service.delete_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
