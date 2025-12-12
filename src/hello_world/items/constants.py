"""Constants for the items domain."""

from enum import StrEnum

# Item field constraints
ITEM_NAME_MIN_LENGTH = 1
ITEM_NAME_MAX_LENGTH = 100
ITEM_DESCRIPTION_MAX_LENGTH = 500
ITEM_PRICE_MIN = 0.01


class ResponseDescriptions(StrEnum):
    """Centralized response descriptions for OpenAPI documentation.

    Using StrEnum ensures type safety and prevents typos in API documentation.
    """

    ITEM_CREATED = "Item created successfully"
    ITEM_RETRIEVED = "Item retrieved successfully"
    ITEMS_RETRIEVED = "Items retrieved successfully"
    ITEM_UPDATED = "Item updated successfully"
    ITEM_DELETED = "Item deleted successfully"
    ITEM_NOT_FOUND = "Item not found"
    ITEM_ALREADY_EXISTS = "Item with this name already exists"
    VALIDATION_ERROR = "Validation error"
