"""Redis client configuration and dependency injection."""

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.core.config import get_settings

# Global redis client instance
_redis_client: Redis | None = None


async def get_redis_client() -> Redis:
    """Get Redis client dependency.

    Returns:
        Redis: Async Redis client instance

    Raises:
        RuntimeError: If Redis client has not been initialized
    """
    if _redis_client is None:
        msg = "Redis client not initialized. Ensure lifespan startup has completed."
        raise RuntimeError(msg)
    return _redis_client


async def init_redis_client() -> Redis:
    """Initialize Redis client from settings.

    Returns:
        Redis: Initialized async Redis client

    Note:
        Uses redis.asyncio.from_url() which automatically manages
        an internal connection pool.
    """
    global _redis_client
    settings = get_settings()
    _redis_client = Redis.from_url(settings.redis_url)
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client and cleanup connection pool.

    Note:
        Must be called on application shutdown to properly
        disconnect connections as there is no asyncio destructor.
    """
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


# Type alias for dependency injection
RedisClient = Annotated[Redis, Depends(get_redis_client)]
