"""Exceptions for the items domain."""

from hello_world.exceptions import HelloWorldError


class ItemNotFoundError(HelloWorldError):
    """Raise when a requested item cannot be found."""

    def __init__(self, item_id: str) -> None:
        """Initialize the exception.

        Args:
            item_id: The ID of the item that was not found
        """
        super().__init__(f"Item with ID '{item_id}' not found")


class ItemAlreadyExistsError(HelloWorldError):
    """Raise when attempting to create an item that already exists."""

    def __init__(self, item_name: str) -> None:
        """Initialize the exception.

        Args:
            item_name: The name of the item that already exists
        """
        super().__init__(f"Item with name '{item_name}' already exists")


class ItemValidationError(HelloWorldError):
    """Raise when item data fails validation."""

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message: Description of the validation error
        """
        super().__init__(message)
