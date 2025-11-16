# Redis Setup Prompt

Using the official redis-py asyncio documentation as context, set up Redis for our FastAPI project.

Documentation to read: FETCH:(https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html)
Focus on: async connection patterns, connection pooling, and FastAPI lifespan integration

First, install dependencies:
```bash
uv add redis
```

Then create/modify these files:

1. UPDATE app/core/config.py:
   - Add `redis_url: str` field to Settings class (after database_url line)

2. CREATE app/core/redis.py with:
   - Singleton redis client using `redis.asyncio.from_url()`
   - `get_redis_client()` dependency function
   - Type hints for Redis client

3. UPDATE app/main.py:
   - Import redis client in lifespan
   - Initialize Redis connection on startup (after logging setup)
   - Close connection on shutdown with `await redis_client.aclose()`

4. UPDATE docker-compose.yml:
   - Add redis service (redis:7-alpine)
   - Port 6379:6379, healthcheck with redis-cli ping
   - Add redis to app depends_on with health condition
   - Add REDIS_URL env var to app service

5. UPDATE .env.example:
   - Add REDIS_URL with both localhost:6379 (local) and redis:6379 (docker) examples

6. CREATE app/core/tests/test_redis.py with:
   - Test redis connection with mock
   - Test get_redis_client dependency

Test requirements:

Unit tests (no external dependencies):
- Test redis client initialization with mocked connection
- Test dependency injection function
- Expected: 2 tests passing

Integration tests (with Redis):
- Test actual redis set/get operations
- Mark with @pytest.mark.integration
- Use docker-compose service
- Expected: 1 test passing

E2E/Manual testing:
- `docker compose up -d redis` → redis container healthy
- `docker compose logs redis` → shows "Ready to accept connections"
- FastAPI startup logs show "redis.connection.initialized"

All linting (ruff check ., mypy app/, pyright app/) must pass

When everything is green, let the user know we are ready to commit

Output format:
Summary: Redis integration complete with async redis-py client
Files created: app/core/redis.py, app/core/tests/test_redis.py
Files modified: app/core/config.py, app/main.py, docker-compose.yml, .env.example
