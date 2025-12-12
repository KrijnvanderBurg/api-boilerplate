"""Items API router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, Response

from hello_world.items import exceptions, schemas
from hello_world.items.dependencies import ItemService, item_service, valid_item_id
from hello_world.items.models import Item
from hello_world.logger import get_logger
from hello_world.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter(tags=["items"])
logger = get_logger(__name__)


# Exception handlers for items domain (registered in main.py but kept here for locality)
async def item_not_found_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemNotFoundError."""
    logger.warning("Item not found", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "type": "ItemNotFoundError"},
    )


async def item_validation_error_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemValidationError."""
    logger.warning("Item validation error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc), "type": "ItemValidationError"},
    )


async def item_already_exists_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemAlreadyExistsError."""
    logger.warning("Item already exists", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "type": "ItemAlreadyExistsError"},
    )


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ItemResponse,
    summary="Create a new item",
    responses={
        201: {"description": "Item created successfully", "model": schemas.ItemResponse},
        422: {"description": "Validation error"},
    },
)
async def create_item(
    item: schemas.ItemCreate,
    item_service: Annotated[ItemService, Depends(item_service)],
) -> schemas.ItemResponse:
    """Create a new item."""
    logger.info("Creating item", item_name=item.name)
    return await item_service.create_item(item)


@router.get(
    "/items",
    response_model=PaginatedResponse[schemas.ItemResponse],
    summary="Read all items",
    responses={
        200: {"description": "Items retrieved successfully"},
    },
)
async def read_items(
    pagination: Annotated[PaginationParams, Depends(PaginationParams)],
    item_service: Annotated[ItemService, Depends(item_service)],
) -> PaginatedResponse[schemas.ItemResponse]:
    """Read all items with pagination."""
    items, total = await item_service.read_items(limit=pagination.limit, offset=pagination.offset)
    return paginate(
        items=items,
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/items/{item_id}",
    response_model=schemas.ItemResponse,
    summary="Read an item by ID",
    responses={
        200: {"description": "Item retrieved successfully", "model": schemas.ItemResponse},
        404: {"description": "Item not found"},
    },
)
async def read_item(
    item: Annotated[schemas.ItemResponse, Depends(valid_item_id)],
) -> schemas.ItemResponse:
    """Read an item by ID. Validation handled by dependency."""
    return item


@router.put(
    "/items/{item_id}",
    response_model=schemas.ItemResponse,
    summary="Update an item",
    responses={
        200: {"description": "Item updated successfully", "model": schemas.ItemResponse},
        404: {"description": "Item not found"},
        422: {"description": "Validation error"},
    },
)
async def update_item(
    item_update: schemas.ItemUpdate,
    item: Annotated[schemas.ItemResponse, Depends(valid_item_id)],
    item_service: Annotated[ItemService, Depends(item_service)],
) -> schemas.ItemResponse:
    """Update an item. Validation handled by dependency."""
    result = await item_service.update_item(item.id, item_update)
    if result is None:
        raise exceptions.ItemNotFoundError(item_id=item.id)
    return result


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    responses={
        204: {"description": "Item deleted successfully"},
        404: {"description": "Item not found"},
    },
)
async def delete_item(
    item: Annotated[Item, Depends(valid_item_id)],
    item_service: Annotated[ItemService, Depends(item_service)],
) -> None:
    """Delete an item. Validation handled by dependency."""
    await item_service.delete_item(item.id)
