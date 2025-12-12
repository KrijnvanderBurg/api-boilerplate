"""Application settings and configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with HELLO_WORLD_ prefix.

    All fields are required and must be provided via environment variables.
    """

    model_config = SettingsConfigDict(
        env_prefix="HELLO_WORLD_",
        case_sensitive=False,
    )

    log_level: str | None = Field(default=None, description="Logging level")
    environment: str | None = Field(default=None, description="Deployment environment")
    app_version: str | None = Field(default=None, description="Application version")
    database_url: str | None = Field(default=None, description="Database URL")
    server_host: str | None = Field(default=None, description="Server host")
    server_port: int | None = Field(default=None, description="Server port")
    cors_origins: list[str] | None = Field(default=None, description="Allowed CORS origins")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern).

    Loads all settings from environment variables with HELLO_WORLD_ prefix.
    Raises ValidationError if any required setting is missing.
    """
    return Settings()
