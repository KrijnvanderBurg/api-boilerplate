"""Item service - business logic for items."""

from uuid import uuid4

from hello_world.models.item import Item, ItemCreate, ItemUpdate


class ItemService:
    """Service for managing items."""

    def __init__(self) -> None:
        """Initialize the service with in-memory storage."""
        self.items_db: dict[str, Item] = {}

    def create_item(self, item: ItemCreate) -> Item:
        """Create a new item."""
        item_id = str(uuid4())
        new_item = Item(id=item_id, **item.model_dump())
        self.items_db[item_id] = new_item
        return new_item

    def list_items(self) -> list[Item]:
        """list all items."""
        return list(self.items_db.values())

    def get_item(self, item_id: str) -> Item | None:
        """Get an item by ID."""
        return self.items_db.get(item_id)

    def update_item(self, item_id: str, item_update: ItemUpdate) -> Item | None:
        """Update an item."""
        if item_id not in self.items_db:
            return None

        existing_item = self.items_db[item_id]
        update_data = item_update.model_dump(exclude_unset=True)
        updated_item = existing_item.model_copy(update=update_data)
        self.items_db[item_id] = updated_item
        return updated_item

    def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        if item_id not in self.items_db:
            return False
        del self.items_db[item_id]
        return True
