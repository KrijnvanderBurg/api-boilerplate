"""Constants for the items domain."""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for items domain."""

    ITEM_NOT_FOUND = "ITEM_NOT_FOUND"
    ITEM_ALREADY_EXISTS = "ITEM_ALREADY_EXISTS"
    ITEM_VALIDATION_ERROR = "ITEM_VALIDATION_ERROR"
    INVALID_ITEM_DATA = "INVALID_ITEM_DATA"


# Item field constraints
ITEM_NAME_MIN_LENGTH = 1
ITEM_NAME_MAX_LENGTH = 100
ITEM_DESCRIPTION_MAX_LENGTH = 500
ITEM_PRICE_MIN = 0.01
