"""Unit tests for Redis client configuration and dependency injection."""

from unittest.mock import AsyncMock, patch

import pytest
from redis.asyncio import Redis

from app.core.redis import (
    close_redis_client,
    get_redis_client,
    init_redis_client,
)


@pytest.mark.asyncio
async def test_init_redis_client():
    """Test Redis client initialization with mocked connection."""
    mock_redis = AsyncMock(spec=Redis)

    with (
        patch("app.core.redis.Redis.from_url") as mock_from_url,
        patch("app.core.redis.get_settings") as mock_settings,
    ):
        # Make from_url return an awaitable that resolves to mock_redis
        mock_from_url.return_value = mock_redis
        mock_settings.return_value.redis_url = "redis://localhost:6379"

        client = await init_redis_client()

        # Verify client was initialized
        assert client is mock_redis

        # Verify from_url was called with correct URL
        mock_from_url.assert_called_once_with("redis://localhost:6379")


@pytest.mark.asyncio
async def test_get_redis_client_dependency():
    """Test get_redis_client dependency function."""
    mock_redis = AsyncMock(spec=Redis)

    # Test when client is not initialized
    with (
        patch("app.core.redis._redis_client", None),
        pytest.raises(RuntimeError, match="Redis client not initialized"),
    ):
        await get_redis_client()

    # Test when client is initialized
    with patch("app.core.redis._redis_client", mock_redis):
        client = await get_redis_client()
        assert client is mock_redis


@pytest.mark.asyncio
async def test_close_redis_client():
    """Test Redis client cleanup and connection closure."""
    mock_redis = AsyncMock(spec=Redis)

    # Test closing initialized client
    with patch("app.core.redis._redis_client", mock_redis):
        await close_redis_client()
        mock_redis.aclose.assert_called_once()

    # Test closing when client is None (should not raise)
    with patch("app.core.redis._redis_client", None):
        await close_redis_client()  # Should not raise


@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_operations():
    """Integration test for actual Redis set/get operations.

    This test requires a running Redis instance and is marked as integration.
    Run with: pytest -m integration
    """
    # Initialize real Redis client
    with patch("app.core.redis.get_settings") as mock_settings:
        mock_settings.return_value.redis_url = "redis://localhost:6379"

        # Initialize client
        client = await init_redis_client()

        try:
            # Test set operation
            await client.set("test_key", "test_value")

            # Test get operation
            value = await client.get("test_key")
            assert value == b"test_value"

            # Test delete operation
            await client.delete("test_key")

            # Verify key is deleted
            value = await client.get("test_key")
            assert value is None

        finally:
            # Cleanup
            await close_redis_client()
