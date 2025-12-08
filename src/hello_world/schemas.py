"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    name: str
    description: str | None = None
    price: float


class ItemUpdate(BaseModel):
    """Schema for updating an item (all fields optional)."""

    name: str | None = None
    description: str | None = None
    price: float | None = None


class Item(ItemCreate):
    """Complete item schema with ID."""

    id: str
