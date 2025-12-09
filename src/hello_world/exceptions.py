"""TODO"""

import enum


class ExitCode(enum.IntEnum):
    """Define standardized exit codes for application termination."""

    SUCCESS = 0
    UNKNOWN_ERROR = 10
    ITEM_NOT_FOUND = 20
    ITEM_VALIDATION_ERROR = 21
    ITEM_ALREADY_EXISTS = 22


class HelloWorldError(Exception):
    """Base exception for all framework-specific errors.

    Associates exceptions with exit codes for CLI integration and provides
    a foundation for granular error handling throughout the pipeline.

    Attributes:
        exit_code: The exit code associated with this exception

    Example:
        >>> try:
        ...     process_pipeline(config)
        ... except HelloWorldError as e:
        ...     sys.exit(e.exit_code)
    """

    def __init__(self, message: str, exit_code: ExitCode) -> None:
        """Initialize the exception with a message and exit code.

        Args:
            message: Description of the error condition
            exit_code: The exit code to report on termination
        """
        self.exit_code = exit_code
        super().__init__(message)


class HelloWorldIOError(HelloWorldError):
    """Raise when file system or I/O operations fail.

    Covers file access, read/write errors, and resource unavailability.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message: Description of the I/O error
        """
        super().__init__(message=message, exit_code=ExitCode.UNKNOWN_ERROR)


class ItemNotFoundError(HelloWorldError):
    """Raise when a requested item cannot be found.

    Used for GET, PUT, DELETE operations on non-existent items.
    """

    def __init__(self, item_id: str) -> None:
        """Initialize the exception.

        Args:
            item_id: The ID of the item that was not found
        """
        super().__init__(message=f"Item with ID '{item_id}' not found", exit_code=ExitCode.ITEM_NOT_FOUND)


class ItemValidationError(HelloWorldError):
    """Raise when item data fails validation.

    Used for business logic validation beyond Pydantic schema validation.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message: Description of the validation error
        """
        super().__init__(message=message, exit_code=ExitCode.ITEM_VALIDATION_ERROR)


class ItemAlreadyExistsError(HelloWorldError):
    """Raise when attempting to create an item that already exists.

    Used for duplicate prevention in create operations.
    """

    def __init__(self, item_name: str) -> None:
        """Initialize the exception.

        Args:
            item_name: The name of the item that already exists
        """
        super().__init__(message=f"Item with name '{item_name}' already exists", exit_code=ExitCode.ITEM_ALREADY_EXISTS)
