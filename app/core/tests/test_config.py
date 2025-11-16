"""Tests for configuration module."""

import os
from unittest.mock import patch

from app.core.config import Settings, get_settings


def test_settings_defaults():
    """Test Settings instantiation with default values."""
    # Clear cache to get fresh instance
    get_settings.cache_clear()

    settings = Settings()
    assert settings.app_name == "Obsidian Agent Project"
    assert settings.version == "0.1.0"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.api_prefix == "/api"
    assert settings.allowed_origins == [
        "http://localhost:3000",
        "http://localhost:8123",
    ]


def test_settings_from_environment():
    """Test Settings loads from environment variables."""
    get_settings.cache_clear()

    with patch.dict(
        os.environ,
        {
            "APP_NAME": "Test App",
            "VERSION": "1.0.0",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "DEBUG",
            "API_PREFIX": "/v1",
        },
        clear=False,
    ):
        settings = Settings()
        assert settings.app_name == "Test App"
        assert settings.version == "1.0.0"
        assert settings.environment == "production"
        assert settings.log_level == "DEBUG"
        assert settings.api_prefix == "/v1"

    get_settings.cache_clear()


def test_get_settings_caching():
    """Test get_settings() returns cached instance."""
    get_settings.cache_clear()

    settings1 = get_settings()
    settings2 = get_settings()

    # Should return the exact same instance
    assert settings1 is settings2

    get_settings.cache_clear()


def test_allowed_origins_default():
    """Test allowed_origins has default values."""
    get_settings.cache_clear()

    settings = Settings()
    assert isinstance(settings.allowed_origins, list)
    assert len(settings.allowed_origins) == 2
    assert "http://localhost:3000" in settings.allowed_origins
    assert "http://localhost:8123" in settings.allowed_origins

    get_settings.cache_clear()
