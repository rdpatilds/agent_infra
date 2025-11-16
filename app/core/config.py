"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Disable JSON parsing for env vars
        env_parse_none_str="null",
    )

    # Application
    app_name: str = "Obsidian Agent Project"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api"

    # Database
    database_url: str

    # CORS - stored as list internally, parsed from comma-separated string
    allowed_origins: list[str] = []

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list[str] | None) -> list[str]:
        """Parse allowed_origins from comma-separated string or list.

        Args:
            v: Either a comma-separated string, a list of strings, or None

        Returns:
            List of origin strings
        """
        if v is None or (isinstance(v, list) and len(v) == 0):
            # Return default values
            return ["http://localhost:3000", "http://localhost:8123"]
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings: Cached settings object loaded from environment.
    """
    return Settings()
