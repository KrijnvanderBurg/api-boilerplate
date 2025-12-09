"""Item service - business logic for items."""

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.items import schemas
from hello_world.items.models import Item
from hello_world.utils import logger as logger_utils

logger = logger_utils.get_logger(__name__)


class ItemService:
    """Service for managing items with PostgreSQL database.

    This service handles all business logic for items using async SQLAlchemy
    to interact with PostgreSQL database without blocking the event loop.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the service with async database session.

        Args:
            db: SQLAlchemy async database session
        """
        self.db = db

    async def create_item(self, item: schemas.ItemCreate) -> schemas.ItemResponse:
        """Create a new item.

        Args:
            item: Item data for creation

        Returns:
            ItemResponse: The created item with ID
        """
        db_item = Item(
            id=str(uuid4()),
            name=item.name,
            description=item.description,
            price=float(item.price),
        )
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        logger.debug("Item created in database", item_id=db_item.id, item_name=db_item.name)
        return schemas.ItemResponse(
            id=db_item.id,
            name=db_item.name,
            description=db_item.description,
            price=db_item.price,
        )

    async def list_items(self, limit: int = 10, offset: int = 0) -> tuple[list[schemas.ItemResponse], int]:
        """List all items with pagination.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            tuple: (list of items, total count)
        """
        # Get total count
        count_result = await self.db.scalar(select(func.count()).select_from(Item))
        total: int = count_result if count_result is not None else 0

        # Get paginated items
        result = await self.db.execute(select(Item).offset(offset).limit(limit))
        items = result.scalars().all()

        response_items = [
            schemas.ItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
            )
            for item in items
        ]

        logger.debug("Items listed", count=len(response_items), total=total)
        return response_items, total

    async def get_item(self, item_id: str) -> schemas.ItemResponse | None:
        """Get an item by ID.

        Args:
            item_id: The unique identifier of the item

        Returns:
            ItemResponse | None: The item if found, None otherwise
        """
        db_item = await self.db.get(Item, item_id)
        if db_item:
            logger.debug("Item retrieved", item_id=item_id)
            return schemas.ItemResponse(
                id=db_item.id,
                name=db_item.name,
                description=db_item.description,
                price=db_item.price,
            )
        return None

    async def update_item(self, item_id: str, item_update: schemas.ItemUpdate) -> schemas.ItemResponse | None:
        """Update an item.

        Args:
            item_id: The unique identifier of the item
            item_update: Updated item data

        Returns:
            ItemResponse | None: The updated item if found, None otherwise
        """
        db_item = await self.db.get(Item, item_id)
        if not db_item:
            logger.debug("Item not found for update", item_id=item_id)
            return None

        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        await self.db.commit()
        await self.db.refresh(db_item)
        logger.debug("Item updated", item_id=item_id, updates=update_data)
        return schemas.ItemResponse(
            id=db_item.id,
            name=db_item.name,
            description=db_item.description,
            price=db_item.price,
        )

    async def delete_item(self, item_id: str) -> bool:
        """Delete an item.

        Args:
            item_id: The unique identifier of the item

        Returns:
            bool: True if item was deleted, False if not found
        """
        db_item = await self.db.get(Item, item_id)
        if not db_item:
            logger.debug("Item not found for deletion", item_id=item_id)
            return False

        await self.db.delete(db_item)
        await self.db.commit()
        logger.debug("Item deleted", item_id=item_id)
        return True
