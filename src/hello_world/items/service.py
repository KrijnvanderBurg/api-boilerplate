"""Item service - business logic layer."""

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.items import schemas
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
        db_item = Item(
            id=str(uuid4()),
            name=item.name,
            description=item.description,
            price=float(item.price),
        )
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        return schemas.ItemResponse.model_validate(db_item)

    async def list_items(self, limit: int = 10, offset: int = 0) -> tuple[list[schemas.ItemResponse], int]:
        """List all items with pagination."""
        count_result = await self.db.scalar(select(func.count(Item.id)))
        total: int = count_result if count_result is not None else 0

        result = await self.db.execute(select(Item).offset(offset).limit(limit))
        items = [schemas.ItemResponse.model_validate(item) for item in result.scalars().all()]
        return items, total

    async def get_item(self, item_id: str) -> schemas.ItemResponse | None:
        """Get an item by ID."""
        db_item = await self.db.get(Item, item_id)
        return schemas.ItemResponse.model_validate(db_item) if db_item else None

    async def update_item(self, item_id: str, item_update: schemas.ItemUpdate) -> schemas.ItemResponse | None:
        """Update an item."""
        db_item = await self.db.get(Item, item_id)
        if not db_item:
            return None

        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)

        await self.db.commit()
        await self.db.refresh(db_item)
        return schemas.ItemResponse.model_validate(db_item)

    async def delete_item(self, item_id: str) -> bool:
        """Delete an item."""
        db_item = await self.db.get(Item, item_id)
        if not db_item:
            return False

        await self.db.delete(db_item)
        await self.db.commit()
        return True
