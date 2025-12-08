"""TODO"""

import enum


class ExitCode(enum.IntEnum):
    """Define standardized exit codes for application termination."""

    SUCCESS = 0
    UNKNOWN_ERROR = 10


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
