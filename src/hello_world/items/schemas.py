"""Pydantic schemas for items domain."""

from pydantic import Field, field_validator

from hello_world.items import constants
from hello_world.models import CustomModel


class ItemCreate(CustomModel):
    """Schema for creating a new item."""

    name: str = Field(
        min_length=constants.ITEM_NAME_MIN_LENGTH,
        max_length=constants.ITEM_NAME_MAX_LENGTH,
        description="Item name",
    )
    description: str | None = Field(
        default=None,
        max_length=constants.ITEM_DESCRIPTION_MAX_LENGTH,
        description="Item description",
    )
    price: float = Field(ge=constants.ITEM_PRICE_MIN, description="Item price (must be positive)")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()


class ItemUpdate(CustomModel):
    """Schema for updating an item (all fields optional)."""

    name: str | None = Field(
        default=None,
        min_length=constants.ITEM_NAME_MIN_LENGTH,
        max_length=constants.ITEM_NAME_MAX_LENGTH,
        description="Item name",
    )
    description: str | None = Field(
        default=None,
        max_length=constants.ITEM_DESCRIPTION_MAX_LENGTH,
        description="Item description",
    )
    price: float | None = Field(default=None, ge=constants.ITEM_PRICE_MIN, description="Item price (must be positive)")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str | None) -> str | None:
        """Validate that name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip() if v else None


class ItemResponse(ItemCreate):
    """Complete item schema with ID."""

    id: str = Field(description="Unique item identifier")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Widget",
                "description": "A useful widget",
                "price": 29.99,
            }
        }
    }
