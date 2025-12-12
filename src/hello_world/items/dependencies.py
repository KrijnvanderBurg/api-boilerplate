"""Dependencies for items domain."""

from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.database import get_db
from hello_world.items import exceptions, schemas
from hello_world.items.service import ItemService
from hello_world.logger import get_logger

logger = get_logger(__name__)


async def item_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ItemService:
    """Dependency for ItemService injection."""
    logger.debug("Creating ItemService instance")
    return ItemService(db)


async def valid_item_id(
    item_id: Annotated[str, Path(description="Item ID")],
    item_service: Annotated[ItemService, Depends(item_service)],
) -> schemas.ItemResponse:
    """Validate item exists and return it."""
    logger.debug("Validating item exists", item_id=item_id)
    item = await item_service.read_item(item_id)
    if not item:
        logger.debug("Item validation failed - not found", item_id=item_id)
        raise exceptions.ItemNotFoundError(item_id)
    logger.debug("Item validated", item_id=item_id)
    return item
