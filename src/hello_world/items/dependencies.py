"""Dependencies for items domain."""

from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.database import get_db
from hello_world.items import exceptions, schemas
from hello_world.items.service import ItemService


async def get_item_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ItemService:
    """Dependency for ItemService injection."""
    return ItemService(db)


async def valid_item_id(
    item_id: Annotated[str, Path(description="Item ID")],
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> schemas.ItemResponse:
    """Validate item exists and return it."""
    item = await item_service.get_item(item_id)
    if not item:
        raise exceptions.ItemNotFoundError(item_id)
    return item
