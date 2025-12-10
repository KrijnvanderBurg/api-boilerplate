"""Application settings and configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with HELLO_WORLD_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="HELLO_WORLD_",
        case_sensitive=False,
    )

    log_level: str | None = Field(default=None, description="Logging level")
    environment: str | None = Field(default=None, description="Deployment environment")
    app_version: str = Field(default="0.1.0", description="Application version")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/hello_world",
        description="Database URL",
    )
    server_host: str = Field(default="127.0.0.1", description="Server host")
    server_port: int = Field(default=8000, description="Server port")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()
