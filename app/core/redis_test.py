"""Simple Redis test endpoints for verification."""

from fastapi import APIRouter

from app.core.redis import RedisClient

router = APIRouter(prefix="/redis-test", tags=["redis-test"])


@router.post("/set/{key}")
async def set_key(key: str, value: str, redis: RedisClient) -> dict[str, str]:
    """Set a key-value pair in Redis.

    Args:
        key: The key to set
        value: The value to store
        redis: Redis client dependency

    Returns:
        dict: Confirmation message with key and value
    """
    await redis.set(key, value)
    return {"message": "Key set successfully", "key": key, "value": value}


@router.get("/get/{key}")
async def get_key(key: str, redis: RedisClient) -> dict[str, str | None]:
    """Get a value from Redis by key.

    Args:
        key: The key to retrieve
        redis: Redis client dependency

    Returns:
        dict: The key and its value (or None if not found)
    """
    value = await redis.get(key)
    return {
        "key": key,
        "value": value.decode() if value else None,
    }


@router.delete("/delete/{key}")
async def delete_key(key: str, redis: RedisClient) -> dict[str, str | int]:
    """Delete a key from Redis.

    Args:
        key: The key to delete
        redis: Redis client dependency

    Returns:
        dict: Confirmation message with deletion count
    """
    deleted = await redis.delete(key)
    return {
        "message": "Key deleted" if deleted else "Key not found",
        "deleted_count": deleted,
    }


@router.get("/ping")
async def ping_redis(redis: RedisClient) -> dict[str, str | bool]:
    """Ping Redis to verify connection.

    Args:
        redis: Redis client dependency

    Returns:
        dict: Connection status
    """
    pong = await redis.ping()
    return {"message": "Redis connection OK", "ping": pong}
