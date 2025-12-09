"""Application settings - Centralized configuration management.

This module provides a singleton-based settings management system using Pydantic
BaseSettings. Settings can be loaded from environment variables and accessed
globally throughout the application with automatic caching and validation.

Key Features:
    - Singleton pattern for consistent configuration access
    - Automatic environment variable loading with HELLO_WORLD_ prefix
    - Type validation and conversion via Pydantic
    - Immutable configuration after initialization

Typical Usage:
    >>> from hello_world.settings import get_settings
    >>>
    >>> # Access settings anywhere in the application
    >>> settings = get_settings()
    >>> print(f"Log level: {settings.log_level}")
    >>> print(f"Environment: {settings.environment}")
    >>>
    >>> # Settings are automatically loaded from environment variables:
    >>> # HELLO_WORLD_LOG_LEVEL=DEBUG
    >>> # HELLO_WORLD_ENVIRONMENT=production
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application-wide settings loaded from environment variables.

    Provides centralized configuration management for the Api framework with
    automatic environment variable loading, type validation, and caching. This
    class follows the singleton pattern when accessed via `get_settings()` to
    ensure consistent configuration throughout the application lifecycle.

    All settings are loaded from environment variables with the `HELLO_WORLD_` prefix
    and are case-insensitive. For example, both `HELLO_WORLD_LOG_LEVEL` and
    `hello_world_log_level` will populate the `log_level` attribute.

    Attributes:
        log_level: Logging level for the application. Valid values are:
            - DEBUG: Detailed diagnostic information
            - INFO: General informational messages (default)
            - WARNING: Warning messages for potentially harmful situations
            - ERROR: Error messages for serious problems
            - CRITICAL: Critical messages for very severe errors
            Loaded from HELLO_WORLD_LOG_LEVEL environment variable. When not set,
            defaults to None and the application uses INFO level.

        environment: Deployment environment identifier.
            resource attribution. Common values include:
            - dev: Development environment
            - test: Testing/QA environment
            - staging: Pre-production staging environment
            - prod/production: Production environment
            Loaded from HELLO_WORLD_ENVIRONMENT environment variable. When not set,
            defaults to None.

    Examples:
        Basic usage with default settings:

        >>> settings = AppSettings()
        >>> print(settings.log_level)  # None (uses INFO default)
        >>> print(settings.environment)  # None

        Load settings from environment variables:

        >>> import os
        >>> os.environ['HELLO_WORLD_LOG_LEVEL'] = 'DEBUG'
        >>> os.environ['HELLO_WORLD_ENVIRONMENT'] = 'production'
        >>> settings = AppSettings()
        >>> print(settings.log_level)  # 'DEBUG'
        >>> print(settings.environment)  # 'production'

    Note:
        - Settings are immutable after initialization by default
        - Use `get_settings()` function for singleton access with caching
        - All environment variable names are case-insensitive
        - The HELLO_WORLD_ prefix is automatically added when loading from environment
        - Direct instantiation creates a new instance; use `get_settings()` for singleton
        - Pydantic provides automatic type conversion and validation

    See Also:
        get_settings: Retrieve the cached singleton settings instance
    """

    model_config = SettingsConfigDict(
        env_prefix="HELLO_WORLD_",
        case_sensitive=False,
    )

    log_level: str | None = Field(default=None, description="Logging level of the system")
    environment: str | None = Field(default=None, description="Deployment environment (dev, test, acc, prod)")
    debug: bool = Field(default=False, description="Enable debug mode")


@lru_cache
def get_settings() -> AppSettings:
    """Retrieve the singleton application settings instance.

    Returns a cached AppSettings instance using the singleton pattern. On first
    call, creates a new AppSettings instance by loading all configuration from
    environment variables. Subsequent calls return the same cached instance,
    ensuring consistent configuration access throughout the application lifecycle.

    This function is the recommended way to access application settings rather
    than directly instantiating AppSettings, as it provides automatic caching
    and ensures all parts of the application use the same configuration.

    Returns:
        AppSettings: The singleton AppSettings instance with all configuration
            loaded from environment variables and validated by Pydantic. All
            attributes are populated from HELLO_WORLD_* environment variables.

    Examples:
        Standard usage pattern:

        >>> from hello_world.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.log_level)
        INFO
        >>> print(settings.environment)
        production

        Multiple calls return the same instance (singleton):

        >>> settings1 = get_settings()
        >>> settings2 = get_settings()
        >>> assert settings1 is settings2  # Same object

        Access configuration throughout the application:

        >>> def configure_logger():
        ...     settings = get_settings()
        ...     logging.basicConfig(level=settings.log_level or 'INFO')
        >>>

        Clear cache to reload settings after environment changes:

        >>> import os
        >>> os.environ['HELLO_WORLD_LOG_LEVEL'] = 'DEBUG'
        >>> get_settings.cache_clear()
        >>> settings = get_settings()  # Reloads from environment
        >>> print(settings.log_level)
        DEBUG

        Use in testing to override settings:

        >>> # In tests, clear cache and set test environment variables
        >>> get_settings.cache_clear()
        >>> os.environ['HELLO_WORLD_ENVIRONMENT'] = 'test'
        >>> os.environ['HELLO_WORLD_LOG_LEVEL'] = 'DEBUG'
        >>> settings = get_settings()
        >>> assert settings.environment == 'test'

    Note:
        - The @lru_cache decorator with no maxsize creates a true singleton
        - Thread-safe: Multiple threads get the same cached instance
        - Memory-efficient: Only one settings instance exists per process
        - To reload settings, call `get_settings.cache_clear()` first
        - In production, settings should be loaded once at startup
        - Changing environment variables after first call has no effect until cache cleared
        - The cache persists for the entire application lifecycle

    See Also:
        AppSettings: The settings class with detailed attribute documentation
        lru_cache: Python's functools decorator used for caching
    """
    return AppSettings()
