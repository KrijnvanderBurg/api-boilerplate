"""Pydantic schemas for items domain."""

from typing import Annotated

from pydantic import AfterValidator, Field

from hello_world.items import constants
from hello_world.models import CustomModel


def validate_name_not_empty(v: str) -> str:
    """Validate that name is not just whitespace."""
    if not v.strip():
        raise ValueError("Name cannot be empty or whitespace")
    return v.strip()


class ItemCreate(CustomModel):
    """Schema for creating a new item."""

    name: Annotated[
        str,
        Field(
            min_length=constants.ITEM_NAME_MIN_LENGTH,
            max_length=constants.ITEM_NAME_MAX_LENGTH,
            description="Item name",
        ),
        AfterValidator(validate_name_not_empty),
    ]
    description: str | None = Field(
        default=None,
        max_length=constants.ITEM_DESCRIPTION_MAX_LENGTH,
        description="Item description",
    )
    price: float = Field(ge=constants.ITEM_PRICE_MIN, description="Item price (must be positive)")


class ItemUpdate(CustomModel):
    """Schema for updating an item (all fields required)."""

    name: Annotated[
        str,
        Field(
            min_length=constants.ITEM_NAME_MIN_LENGTH,
            max_length=constants.ITEM_NAME_MAX_LENGTH,
            description="Item name",
        ),
        AfterValidator(validate_name_not_empty),
    ]
    description: str | None = Field(
        default=None,
        max_length=constants.ITEM_DESCRIPTION_MAX_LENGTH,
        description="Item description",
    )
    price: float = Field(ge=constants.ITEM_PRICE_MIN, description="Item price (must be positive)")


class ItemResponse(ItemCreate):
    """Complete item schema with ID."""

    id: str = Field(description="Unique item identifier")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Widget",
                "description": "A useful widget",
                "price": 29.99,
            }
        },
    }
