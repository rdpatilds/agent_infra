# Step-by-Step Startup Guide

This guide provides detailed instructions for starting the FastAPI application with Redis and PostgreSQL.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.13+ installed
- `uv` package manager installed

## Option 1: Start Everything with Docker Compose (Recommended)

This starts Redis, PostgreSQL, and the FastAPI app all together in containers.

### Step 1: Start all services

```bash
docker compose up -d
```

This command starts:
- Redis (port 6379)
- PostgreSQL (port 5433)
- FastAPI app (port 8123)

### Step 2: Verify services are running

```bash
docker compose ps
```

Expected output:
```
NAME             IMAGE                      STATUS                   PORTS
obsidian-db      postgres:18-alpine         Up (healthy)             0.0.0.0:5433->5432/tcp
obsidian-redis   redis:7-alpine             Up (healthy)             0.0.0.0:6379->6379/tcp
live-template-build  live-template-build:latest  Up                  0.0.0.0:8123->8123/tcp
```

### Step 3: View logs

```bash
# View all service logs
docker compose logs -f

# Or view logs from specific service
docker compose logs -f app
docker compose logs -f redis
docker compose logs -f db
```

### Step 4: Test the application

```bash
# Test Redis connection
curl http://localhost:8123/redis-test/ping

# Test health endpoints
curl http://localhost:8123/health
curl http://localhost:8123/health/db

# Open API documentation in browser
# http://localhost:8123/docs
```

---

## Option 2: Start Services Individually (Local Development)

This runs Redis and PostgreSQL in Docker, but FastAPI locally. This is useful for development with hot-reload and debugging.

### Step 1: Ensure you have a .env file

```bash
# Copy the example if you don't have one
cp .env.example .env
```

Verify the `.env` file contains:
```
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db
```

### Step 2: Start Redis

```bash
docker compose up -d redis
```

### Step 3: Start PostgreSQL

```bash
docker compose up -d db
```

### Step 4: Verify Docker services are healthy

```bash
docker compose ps
```

Wait until both services show "Up (healthy)" status:
```
NAME             IMAGE                STATUS                   PORTS
obsidian-db      postgres:18-alpine   Up (healthy)             0.0.0.0:5433->5432/tcp
obsidian-redis   redis:7-alpine       Up (healthy)             0.0.0.0:6379->6379/tcp
```

### Step 5: Start FastAPI locally

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8123 --reload
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/home/user/projects/agent_infra']
INFO:     Uvicorn running on http://0.0.0.0:8123 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
{"event": "application.startup", "level": "info", ...}
{"event": "database.connection.initialized", "level": "info", ...}
{"event": "redis.connection.initialized", "level": "info", ...}
INFO:     Application startup complete.
```

### Step 6: Test the application

Open a new terminal and run:

```bash
# Test Redis connection
curl http://localhost:8123/redis-test/ping

# Test health endpoints
curl http://localhost:8123/health
curl http://localhost:8123/health/db

# Open API documentation in browser
# http://localhost:8123/docs
```

---

## Verification & Testing

### Basic Health Checks

```bash
# Root endpoint
curl http://localhost:8123/

# Health check
curl http://localhost:8123/health

# Database health check
curl http://localhost:8123/health/db
```

### Redis Test Commands

```bash
# 1. Ping Redis
curl http://localhost:8123/redis-test/ping

# 2. Set a key-value pair
curl -X POST "http://localhost:8123/redis-test/set/mykey?value=hello-world"

# 3. Get the value
curl http://localhost:8123/redis-test/get/mykey

# 4. Delete the key
curl -X DELETE http://localhost:8123/redis-test/delete/mykey

# 5. Verify deletion
curl http://localhost:8123/redis-test/get/mykey
```

### Full Test Sequence

```bash
# Test connection
echo "=== Testing Redis Connection ==="
curl http://localhost:8123/redis-test/ping
echo -e "\n"

# Set a key
echo "=== Setting key 'user:123' ==="
curl -X POST "http://localhost:8123/redis-test/set/user:123?value=john_doe"
echo -e "\n"

# Get the key
echo "=== Getting key 'user:123' ==="
curl http://localhost:8123/redis-test/get/user:123
echo -e "\n"

# Set another key
echo "=== Setting key 'session:abc' ==="
curl -X POST "http://localhost:8123/redis-test/set/session:abc?value=active"
echo -e "\n"

# Get the second key
echo "=== Getting key 'session:abc' ==="
curl http://localhost:8123/redis-test/get/session:abc
echo -e "\n"

# Delete first key
echo "=== Deleting key 'user:123' ==="
curl -X DELETE http://localhost:8123/redis-test/delete/user:123
echo -e "\n"

# Verify deletion
echo "=== Verifying 'user:123' is deleted ==="
curl http://localhost:8123/redis-test/get/user:123
echo -e "\n"

# Verify second key still exists
echo "=== Verifying 'session:abc' still exists ==="
curl http://localhost:8123/redis-test/get/session:abc
echo -e "\n"
```

---

## Shutdown Commands

### Option 1: Stop all Docker Compose services

```bash
docker compose down
```

This stops and removes all containers, networks, but preserves volumes (database data).

### Option 2: Stop individual services

```bash
# Stop specific service
docker compose stop redis
docker compose stop db
docker compose stop app

# Or restart specific service
docker compose restart redis
```

### Option 3: Stop local FastAPI

If running FastAPI locally (Option 2), press `Ctrl+C` in the terminal where uvicorn is running.

---

## Troubleshooting

### Port Already in Use

If you see errors about ports being in use:

```bash
# Check what's using the ports
lsof -i :6379  # Redis
lsof -i :5433  # PostgreSQL
lsof -i :8123  # FastAPI

# Kill processes if needed
kill -9 <PID>
```

### Services Not Healthy

```bash
# View detailed logs
docker compose logs redis
docker compose logs db
docker compose logs app

# Check service status
docker compose ps

# Restart specific service
docker compose restart redis
docker compose restart db
```

### Redis Connection Errors

```bash
# Check Redis is running
docker compose ps redis

# Test Redis directly with redis-cli
docker exec -it obsidian-redis redis-cli ping
# Should return: PONG

# Check application logs
docker compose logs app | grep redis
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker compose ps db

# Test PostgreSQL connection
docker exec -it obsidian-db pg_isready -U postgres
# Should return: /var/run/postgresql:5432 - accepting connections

# Check application logs
docker compose logs app | grep database
```

### Clear Everything and Start Fresh

```bash
# Stop and remove all containers, networks, and volumes
docker compose down -v

# Remove built images (optional)
docker compose down --rmi all -v

# Start fresh
docker compose up -d
```

---

## Development Workflow

### Recommended Setup for Development

1. Start dependencies in Docker:
   ```bash
   docker compose up -d redis db
   ```

2. Run FastAPI locally for hot-reload:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8123 --reload
   ```

3. Make code changes - the server will auto-reload

4. Run tests:
   ```bash
   # Unit tests only
   uv run pytest -m "not integration"

   # All tests including integration
   uv run pytest
   ```

5. When done, stop Docker services:
   ```bash
   docker compose stop redis db
   ```

---

## Quick Reference

| Service    | Port  | Docker Container    | Health Check                              |
|------------|-------|---------------------|-------------------------------------------|
| FastAPI    | 8123  | live-template-build | `curl http://localhost:8123/health`       |
| Redis      | 6379  | obsidian-redis      | `docker exec obsidian-redis redis-cli ping` |
| PostgreSQL | 5433  | obsidian-db         | `docker exec obsidian-db pg_isready -U postgres` |

### Environment Variables

| Variable      | Local Development       | Docker                  |
|---------------|-------------------------|-------------------------|
| REDIS_URL     | redis://localhost:6379  | redis://redis:6379      |
| DATABASE_URL  | ...@localhost:5433/...  | ...@db:5432/...         |

### Important URLs

- API Documentation (Swagger): http://localhost:8123/docs
- API Documentation (ReDoc): http://localhost:8123/redoc
- Health Check: http://localhost:8123/health
- Database Health: http://localhost:8123/health/db
- Redis Test: http://localhost:8123/redis-test/ping

---

## Next Steps

After starting the application:

1. Explore the API documentation at http://localhost:8123/docs
2. Test Redis operations using the `/redis-test/*` endpoints
3. Check database health at http://localhost:8123/health/db
4. Start building your features using the Redis client via dependency injection
5. Add your own endpoints that use Redis for caching, sessions, etc.

For more information about the Redis integration, see the official documentation:
- [redis-py async examples](https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html)
