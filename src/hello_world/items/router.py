"""Items API router.

This router handles all item-related endpoints following FastAPI best practices:
- Async route handlers for I/O operations
- Dependencies for validation and service injection
- Comprehensive response documentation
- Proper status codes and error handling
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, Response

from hello_world.items import dependencies, schemas
from hello_world.logger import get_logger
from hello_world.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter(prefix="/items", tags=["items"])
logger = get_logger(__name__)


# Exception handlers for items domain
async def item_not_found_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemNotFoundError exceptions.

    Args:
        request: The incoming request
        exc: The ItemNotFoundError exception

    Returns:
        Response: Error response with 404 status
    """
    logger.warning(
        "Item not found",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "type": "ItemNotFoundError",
        },
    )


async def item_validation_error_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemValidationError exceptions.

    Args:
        request: The incoming request
        exc: The ItemValidationError exception

    Returns:
        Response: Error response with 422 status
    """
    logger.warning(
        "Item validation error",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "type": "ItemValidationError",
        },
    )


async def item_already_exists_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemAlreadyExistsError exceptions.

    Args:
        request: The incoming request
        exc: The ItemAlreadyExistsError exception

    Returns:
        Response: Error response with 409 status
    """
    logger.warning(
        "Item already exists",
        error=str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": str(exc),
            "type": "ItemAlreadyExistsError",
        },
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ItemResponse,
    summary="Create a new item",
    description="Create a new item with the provided name, description, and price.",
    responses={
        201: {
            "description": "Item created successfully",
            "model": schemas.ItemResponse,
        },
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
    },
)
async def create_item(
    item: schemas.ItemCreate,
    item_service: Annotated[dependencies.service.ItemService, Depends(dependencies.get_item_service)],
) -> schemas.ItemResponse:
    """Create a new item."""
    logger.info("Creating item", item_name=item.name, price=item.price)
    created_item = await item_service.create_item(item)
    logger.info("Item created successfully", item_id=created_item.id)
    return created_item


@router.get(
    "",
    response_model=PaginatedResponse[schemas.ItemResponse],
    summary="List all items",
    description="Retrieve a paginated list of all items in the system.",
    responses={
        200: {
            "description": "List of items retrieved successfully",
            "model": PaginatedResponse[schemas.ItemResponse],
        },
    },
)
async def list_items(
    pagination: Annotated[PaginationParams, Depends()],
    item_service: Annotated[dependencies.service.ItemService, Depends(dependencies.get_item_service)],
) -> PaginatedResponse[schemas.ItemResponse]:
    """List all items with pagination."""
    logger.info("Listing items", limit=pagination.limit, offset=pagination.offset)
    items, total = await item_service.list_items(limit=pagination.limit, offset=pagination.offset)
    logger.info("Items retrieved", count=len(items), total=total)
    return paginate(items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get(
    "/{item_id}",
    response_model=schemas.ItemResponse,
    summary="Get an item by ID",
    description="Retrieve a specific item by its unique identifier.",
    responses={
        200: {
            "description": "Item retrieved successfully",
            "model": schemas.ItemResponse,
        },
        404: {"description": "Item not found"},
    },
)
async def get_item(
    item: Annotated[schemas.ItemResponse, Depends(dependencies.valid_item_id)],
) -> schemas.ItemResponse:
    """Get an item by ID.

    The item is validated and retrieved by the valid_item_id dependency,
    demonstrating FastAPI's dependency injection and caching capabilities.
    """
    logger.info("Item retrieved", item_id=item.id)
    return item


@router.put(
    "/{item_id}",
    response_model=schemas.ItemResponse,
    summary="Update an item",
    description="Update an existing item with new data. Only provided fields will be updated.",
    responses={
        200: {
            "description": "Item updated successfully",
            "model": schemas.ItemResponse,
        },
        404: {"description": "Item not found"},
        400: {"description": "Invalid input data"},
        422: {"description": "Validation error"},
    },
)
async def update_item(
    item_update: schemas.ItemUpdate,
    item: Annotated[schemas.ItemResponse, Depends(dependencies.valid_item_id)],
    item_service: Annotated[dependencies.service.ItemService, Depends(dependencies.get_item_service)],
) -> schemas.ItemResponse:
    """Update an item.

    The valid_item_id dependency ensures the item exists before attempting update.
    This demonstrates dependency chaining for validation.
    """
    logger.info("Updating item", item_id=item.id, update_data=item_update.model_dump(exclude_unset=True))
    updated_item = await item_service.update_item(item.id, item_update)
    # This should not be None because valid_item_id already validated existence
    logger.info("Item updated successfully", item_id=item.id)
    return updated_item  # type: ignore


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    description="Delete an existing item by its unique identifier.",
    responses={
        204: {"description": "Item deleted successfully"},
        404: {"description": "Item not found"},
    },
)
async def delete_item(
    item: Annotated[schemas.ItemResponse, Depends(dependencies.valid_item_id)],
    item_service: Annotated[dependencies.service.ItemService, Depends(dependencies.get_item_service)],
) -> None:
    """Delete an item.

    The valid_item_id dependency ensures the item exists before attempting deletion.
    """
    logger.info("Deleting item", item_id=item.id)
    await item_service.delete_item(item.id)
    logger.info("Item deleted successfully", item_id=item.id)
