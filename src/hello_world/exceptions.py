"""Global exceptions for the application."""


class HelloWorldError(Exception):
    """Base exception for all application-specific errors.

    Provides a foundation for granular error handling throughout the application.

    Example:
        >>> try:
        ...     process_data()
        ... except HelloWorldError as e:
        ...     logger.error(f"Application error: {e}")
    """
