"""Items API router."""

from fastapi import APIRouter, HTTPException, Path, status

from hello_world.models.item import Item, ItemCreate, ItemUpdate
from hello_world.services.item_service import ItemService
from hello_world.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
item_service = ItemService()


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=Item,
    summary="Create a new item",
    description="Create a new item with the provided name, description, and price.",
    responses={
        201: {"description": "Item created successfully"},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
    },
)
def create_item(
    item: ItemCreate,
) -> Item:
    """Create a new item."""
    logger.info("Creating item", item_name=item.name, price=item.price)
    created_item = item_service.create_item(item)
    logger.info("Item created successfully", item_id=created_item.id)
    return created_item


@router.get(
    "/items",
    response_model=list[Item],
    summary="List all items",
    description="Retrieve a list of all items in the system.",
    responses={
        200: {"description": "List of items retrieved successfully"},
    },
)
def list_items() -> list[Item]:
    """List all items."""
    logger.info("Listing all items")
    items = item_service.list_items()
    logger.info("Items retrieved", count=len(items))
    return items


@router.get(
    "/items/{item_id}",
    response_model=Item,
    summary="Get an item by ID",
    description="Retrieve a specific item by its unique identifier.",
    responses={
        200: {"description": "Item retrieved successfully"},
        404: {"description": "Item not found"},
    },
)
def get_item(
    item_id: str = Path(..., min_length=1, description="The unique identifier of the item"),
) -> Item:
    """Get an item by ID."""
    logger.info("Retrieving item", item_id=item_id)
    item = item_service.get_item(item_id)
    if not item:
        logger.warning("Item not found", item_id=item_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    logger.info("Item retrieved successfully", item_id=item_id)
    return item


@router.put(
    "/items/{item_id}",
    response_model=Item,
    summary="Update an item",
    description="Update an existing item with new data. Only provided fields will be updated.",
    responses={
        200: {"description": "Item updated successfully"},
        404: {"description": "Item not found"},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
    },
)
def update_item(
    item_update: ItemUpdate,
    item_id: str = Path(..., min_length=1, description="The unique identifier of the item"),
) -> Item:
    """Update an item."""
    logger.info("Updating item", item_id=item_id, update_data=item_update.model_dump(exclude_unset=True))
    item = item_service.update_item(item_id, item_update)
    if not item:
        logger.warning("Item not found for update", item_id=item_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    logger.info("Item updated successfully", item_id=item_id)
    return item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description="Delete an existing item by its unique identifier.",
    responses={
        204: {"description": "Item deleted successfully"},
        404: {"description": "Item not found"},
    },
)
def delete_item(
    item_id: str = Path(..., min_length=1, description="The unique identifier of the item"),
) -> None:
    """Delete an item."""
    logger.info("Deleting item", item_id=item_id)
    if not item_service.delete_item(item_id):
        logger.warning("Item not found for deletion", item_id=item_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    logger.info("Item deleted successfully", item_id=item_id)
