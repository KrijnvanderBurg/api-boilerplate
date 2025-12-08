"""FastAPI application - simple boilerplate."""

from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from hello_world.api.schemas import Item, ItemCreate, ItemUpdate

app = FastAPI(
    title="Hello World API",
    description="A simple FastAPI boilerplate",
    version="0.1.0",
)

# In-memory storage
items_db: Dict[str, Item] = {}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/items", status_code=201)
async def create_item(item: ItemCreate) -> Item:
    """Create a new item."""
    item_id = str(uuid4())
    new_item = Item(id=item_id, **item.model_dump())
    items_db[item_id] = new_item
    return new_item


@app.get("/items")
async def list_items() -> List[Item]:
    """List all items."""
    return list(items_db.values())


@app.get("/items/{item_id}")
async def get_item(item_id: str) -> Item:
    """Get an item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.put("/items/{item_id}")
async def update_item(item_id: str, item_update: ItemUpdate) -> Item:
    """Update an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_item = items_db[item_id]
    update_data = item_update.model_dump(exclude_unset=True)
    updated_item = existing_item.model_copy(update=update_data)
    items_db[item_id] = updated_item
    return updated_item


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
