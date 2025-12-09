"""Dependencies for items domain.

Dependencies are used for request validation, authentication, authorization,
and other cross-cutting concerns. FastAPI caches dependency results within
a request scope for efficient reuse.
"""

from typing import Annotated

from fastapi import Depends, Path

from hello_world.items import exceptions, schemas, service
from hello_world.utils import logger as logger_utils

logger = logger_utils.get_logger(__name__)

# Singleton service instance for in-memory storage
_item_service_instance: service.ItemService | None = None


async def get_item_service() -> service.ItemService:
    """Dependency injection for ItemService.

    Returns a singleton instance to maintain in-memory state across requests.
    For production use with a database, this would create a new instance per request.

    Returns:
        ItemService: The singleton ItemService instance
    """
    global _item_service_instance
    if _item_service_instance is None:
        _item_service_instance = service.ItemService()
    return _item_service_instance


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
