"""Global configuration settings.

This module provides the main application configuration based on FastAPI best practices.
Domain-specific configurations are decoupled into separate config modules.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Global application configuration.

    Main configuration class for the application. Domain-specific configurations
    should be defined in their respective domain modules (e.g., items/config.py).

    Attributes:
        environment: Deployment environment (local, staging, production)
        app_version: Application version
        site_domain: Domain name of the site
    """

    model_config = SettingsConfigDict(
        env_prefix="HELLO_WORLD_",
        case_sensitive=False,
    )

    environment: str = Field(default="local", description="Deployment environment")
    app_version: str = Field(default="0.1.0", description="Application version")
    site_domain: str = Field(default="localhost:8000", description="Site domain")
    log_level: str = Field(default="INFO", description="Logging level")


@lru_cache
def get_config() -> Config:
    """Get cached global configuration instance.

    Returns:
        Config: The singleton Config instance
    """
    return Config()
