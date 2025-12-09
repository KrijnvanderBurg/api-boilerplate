"""Item service - business logic for items."""

from uuid import uuid4

from hello_world.items import schemas
from hello_world.utils import logger as logger_utils

logger = logger_utils.get_logger(__name__)


class ItemService:
    """Service for managing items.

    This service handles all business logic for items. In production,
    this would interact with a database instead of in-memory storage.
    """

    def __init__(self) -> None:
        """Initialize the service with in-memory storage."""
        self.items_db: dict[str, schemas.ItemResponse] = {}

    async def create_item(self, item: schemas.ItemCreate) -> schemas.ItemResponse:
        """Create a new item.

        Args:
            item: Item data for creation

        Returns:
            ItemResponse: The created item with ID
        """
        item_id = str(uuid4())
        new_item = schemas.ItemResponse(id=item_id, **item.model_dump())
        self.items_db[item_id] = new_item
        logger.debug("Item created in service", item_id=item_id, item_name=new_item.name)
        return new_item

    async def list_items(self, limit: int = 10, offset: int = 0) -> tuple[list[schemas.ItemResponse], int]:
        """List all items with pagination.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            tuple: (list of items, total count)
        """
        all_items = list(self.items_db.values())
        total = len(all_items)
        paginated_items = all_items[offset : offset + limit]
        logger.debug("Items listed", count=len(paginated_items), total=total)
        return paginated_items, total

    async def get_item(self, item_id: str) -> schemas.ItemResponse | None:
        """Get an item by ID.

        Args:
            item_id: The unique identifier of the item

        Returns:
            ItemResponse | None: The item if found, None otherwise
        """
        item = self.items_db.get(item_id)
        if item:
            logger.debug("Item retrieved", item_id=item_id)
        return item

    async def update_item(self, item_id: str, item_update: schemas.ItemUpdate) -> schemas.ItemResponse | None:
        """Update an item.

        Args:
            item_id: The unique identifier of the item
            item_update: Updated item data

        Returns:
            ItemResponse | None: The updated item if found, None otherwise
        """
        if item_id not in self.items_db:
            logger.debug("Item not found for update", item_id=item_id)
            return None

        existing_item = self.items_db[item_id]
        update_data = item_update.model_dump(exclude_unset=True)
        updated_item = existing_item.model_copy(update=update_data)
        self.items_db[item_id] = updated_item
        logger.debug("Item updated", item_id=item_id, updates=update_data)
        return updated_item

    async def delete_item(self, item_id: str) -> bool:
        """Delete an item.

        Args:
            item_id: The unique identifier of the item

        Returns:
            bool: True if item was deleted, False if not found
        """
        if item_id not in self.items_db:
            logger.debug("Item not found for deletion", item_id=item_id)
            return False
        del self.items_db[item_id]
        logger.debug("Item deleted", item_id=item_id)
        return True
