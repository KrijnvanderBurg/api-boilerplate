"""Dependencies for items domain.

Dependencies are used for request validation, authentication, authorization,
and other cross-cutting concerns. FastAPI caches dependency results within
a request scope for efficient reuse.
"""

from typing import Annotated

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.database import get_db
from hello_world.items import exceptions, schemas, service
from hello_world.logger import get_logger

logger = get_logger(__name__)


async def get_item_service(db: Annotated[AsyncSession, Depends(get_db)]) -> service.ItemService:
    """Dependency injection for ItemService.

    Creates a new ItemService instance with the async database session for each request.

    Args:
        db: Async database session dependency

    Returns:
        ItemService: The ItemService instance with async database session
    """
    return service.ItemService(db)


async def valid_item_id(
    item_id: Annotated[str, Path(min_length=1, description="The unique identifier of the item")],
    item_service: Annotated[service.ItemService, Depends(get_item_service)],
) -> schemas.ItemResponse:
    """Validate that an item exists and return it.

    This dependency validates the item_id and returns the item if found.
    It demonstrates the FastAPI best practice of using dependencies for
    validation instead of doing it in route handlers.

    Args:
        item_id: The unique identifier of the item
        item_service: The ItemService dependency (cached per request)

    Returns:
        ItemResponse: The validated item

    Raises:
        ItemNotFoundError: If the item does not exist
    """
    logger.debug("Validating item ID", item_id=item_id)
    item = await item_service.get_item(item_id)
    if not item:
        logger.warning("Item not found in validation", item_id=item_id)
        raise exceptions.ItemNotFoundError(item_id)
    return item
