"""Items API router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, Response

from hello_world.items import exceptions, schemas
from hello_world.items.constants import ResponseDescriptions
from hello_world.items.dependencies import ItemService, item_service, valid_item_id
from hello_world.items.models import Item
from hello_world.logger import get_logger
from hello_world.pagination import PaginatedResponse, PaginationParams, paginate

logger = get_logger(__name__)
router = APIRouter(tags=["items"])


# Exception handlers for items domain (registered in main.py but kept here for locality)
async def item_not_found_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemNotFoundError."""
    logger.warning(
        "Item not found",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


async def item_validation_error_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemValidationError."""
    logger.warning(
        "Item validation failed",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


async def item_already_exists_handler(request: Request, exc: Exception) -> Response:
    """Handle ItemAlreadyExistsError."""
    logger.warning(
        "Item already exists",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "type": type(exc).__name__},
    )


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ItemResponse,
    summary="Create a new item",
    responses={
        201: {"description": ResponseDescriptions.ITEM_CREATED, "model": schemas.ItemResponse},
        422: {"description": ResponseDescriptions.VALIDATION_ERROR},
    },
)
async def create_item(
    item: schemas.ItemCreate,
    service: Annotated[ItemService, Depends(item_service)],
) -> schemas.ItemResponse:
    """Create a new item."""
    logger.debug("Creating item request received", item_name=item.name, price=item.price)
    result = await service.create_item(item)
    logger.info("Item created", item_id=result.id, item_name=result.name)
    return result


@router.get(
    "/items",
    response_model=PaginatedResponse[schemas.ItemResponse],
    summary="Read all items",
    responses={
        200: {"description": ResponseDescriptions.ITEMS_RETRIEVED},
    },
)
async def read_items(
    pagination: Annotated[PaginationParams, Depends(PaginationParams)],
    service: Annotated[ItemService, Depends(item_service)],
) -> PaginatedResponse[schemas.ItemResponse]:
    """Read all items with pagination."""
    logger.debug("Fetching items", limit=pagination.limit, offset=pagination.offset)
    items, total = await service.read_items(limit=pagination.limit, offset=pagination.offset)
    logger.info("Items retrieved", count=len(items), total=total, limit=pagination.limit, offset=pagination.offset)
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
        200: {"description": ResponseDescriptions.ITEM_RETRIEVED, "model": schemas.ItemResponse},
        404: {"description": ResponseDescriptions.ITEM_NOT_FOUND},
    },
)
async def read_item(
    item: Annotated[schemas.ItemResponse, Depends(valid_item_id)],
) -> schemas.ItemResponse:
    """Read an item by ID. Validation handled by dependency."""
    logger.debug("Item retrieved", item_id=item.id, item_name=item.name)
    return item


@router.put(
    "/items/{item_id}",
    response_model=schemas.ItemResponse,
    summary="Update an item",
    responses={
        200: {"description": ResponseDescriptions.ITEM_UPDATED, "model": schemas.ItemResponse},
        404: {"description": ResponseDescriptions.ITEM_NOT_FOUND},
        422: {"description": ResponseDescriptions.VALIDATION_ERROR},
    },
)
async def update_item(
    item_update: schemas.ItemUpdate,
    item: Annotated[schemas.ItemResponse, Depends(valid_item_id)],
    service: Annotated[ItemService, Depends(item_service)],
) -> schemas.ItemResponse:
    """Update an item. Validation handled by dependency."""
    logger.debug("Updating item", item_id=item.id, new_name=item_update.name, new_price=item_update.price)
    result = await service.update_item(item.id, item_update)
    if result is None:
        logger.error("Item not found after validation passed", item_id=item.id)
        raise exceptions.ItemNotFoundError(item_id=item.id)
    logger.info("Item updated", item_id=result.id, item_name=result.name)
    return result


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    responses={
        204: {"description": ResponseDescriptions.ITEM_DELETED},
        404: {"description": ResponseDescriptions.ITEM_NOT_FOUND},
    },
)
async def delete_item(
    item: Annotated[Item, Depends(valid_item_id)],
    service: Annotated[ItemService, Depends(item_service)],
) -> None:
    """Delete an item. Validation handled by dependency."""
    logger.debug("Deleting item", item_id=item.id, item_name=item.name)
    await service.delete_item(item.id)
    logger.info("Item deleted", item_id=item.id)
