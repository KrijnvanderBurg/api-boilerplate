"""Item service - business logic layer."""

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.items import schemas
from hello_world.items.exceptions import ItemAlreadyExistsError
from hello_world.items.models import Item
from hello_world.logger import get_logger

logger = get_logger(__name__)


class ItemService:
    """Service for item business logic."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize with database session."""
        self.db = db

    async def create_item(self, item: schemas.ItemCreate) -> schemas.ItemResponse:
        """Create a new item."""
        item_id = str(uuid4())
        logger.debug(
            "Creating new item in database",
            item_id=item_id,
            name=item.name,
            description=item.description,
            price=item.price,
        )
        db_item = Item(
            id=item_id,
            name=item.name,
            description=item.description,
            price=float(item.price),
        )
        self.db.add(db_item)
        try:
            await self.db.commit()
            logger.debug("Item committed to database", item_id=item_id)
            await self.db.refresh(db_item)
            return schemas.ItemResponse.model_validate(db_item)
        except IntegrityError:
            await self.db.rollback()
            logger.debug("Duplicate item name detected", name=item.name)
            raise ItemAlreadyExistsError(item.name)

    async def read_items(self, limit: int = 10, offset: int = 0) -> tuple[list[schemas.ItemResponse], int]:
        """Read all items with pagination."""
        logger.debug("Querying database for items", limit=limit, offset=offset)
        count_result = await self.db.scalar(select(func.count(Item.id)))
        total: int = count_result if count_result is not None else 0
        logger.debug("Total items in database", total=total)

        result = await self.db.execute(select(Item).offset(offset).limit(limit))
        items = [schemas.ItemResponse.model_validate(item) for item in result.scalars().all()]
        logger.debug("Items fetched from database", count=len(items))
        return items, total

    async def read_item(self, item_id: str) -> schemas.ItemResponse | None:
        """Read an item by ID."""
        logger.debug("Fetching item from database", item_id=item_id)
        db_item = await self.db.get(Item, item_id)
        if db_item:
            logger.debug("Item found in database", item_id=item_id, name=db_item.name)
        else:
            logger.debug("Item not found in database", item_id=item_id)
        return schemas.ItemResponse.model_validate(db_item) if db_item else None

    async def update_item(self, item_id: str, item_update: schemas.ItemUpdate) -> schemas.ItemResponse | None:
        """Update an item."""
        logger.debug("Fetching item for update", item_id=item_id)
        existing_item = await self.db.get(Item, item_id)
        if not existing_item:
            logger.debug("Item not found for update", item_id=item_id)
            return None

        logger.debug(
            "Updating item fields",
            item_id=item_id,
            old_name=existing_item.name,
            new_name=item_update.name,
            old_price=existing_item.price,
            new_price=item_update.price,
        )
        existing_item.name = item_update.name
        existing_item.description = item_update.description
        existing_item.price = float(item_update.price)

        try:
            await self.db.commit()
            logger.debug("Item update committed to database", item_id=item_id)
            await self.db.refresh(existing_item)
            return schemas.ItemResponse.model_validate(existing_item)
        except IntegrityError:
            await self.db.rollback()
            logger.debug("Duplicate item name detected during update", name=item_update.name, item_id=item_id)
            raise ItemAlreadyExistsError(item_update.name)

    async def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        logger.debug("Fetching item for deletion", item_id=item_id)
        db_item = await self.db.get(Item, item_id)
        if not db_item:
            logger.debug("Item not found for deletion", item_id=item_id)
            return False

        logger.debug("Deleting item from database", item_id=item_id, name=db_item.name)
        await self.db.delete(db_item)
        await self.db.commit()
        logger.debug("Item deletion committed to database", item_id=item_id)
        return True
