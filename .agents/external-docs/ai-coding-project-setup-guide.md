---
description: Instructor guide for setting up the Obsidian Agent project during video recording
---

# Obsidian Agent Project Setup

## Choose Your Programming Language and Tooling

Before diving into the setup, you need to pick your programming language and core tooling. If you're unsure, ask your AI coding assistant to help you evaluate what's best for your specific use case.

**Recommended Languages:**
- **Python** - Excellent for data processing, ML/AI, automation, and backend APIs. If you choose Python, I recommend using [uv](https://docs.astral.sh/uv/) as your package manager and project tool. It's fast, modern, and handles virtual environments seamlessly.
- **TypeScript** - Great for full-stack development with strong type safety. Your tooling will depend on what you're building:
  - Frontend: React, Next.js, Vue, Svelte
  - Backend: Express, Fastify, NestJS
  - Full-stack: Next.js, Remix, T3 Stack

**This guide assumes you're using Python with uv.** If you're using a different language or stack, have your AI coding assistant help you adapt this guide's principles (structured prompts, linting, type checking, testing, Docker setup) to your chosen tools.

## Initialize the Project

```bash
uv init obsidian-agent-project
cd obsidian-agent-project
code .
```

## Verify Installation

To check that it starts correctly, run the following command in your terminal.

To open your terminal in most IDEs you can do `cmd + J` or `ctrl + J`, then type:

```bash
uv run main.py
```

It should print:

```
Your python version
Creating virtual environment at: .venv
Hello from obsidian-agent-project!
```

## Set Up GitHub Repository

Go to GitHub. If you don't have an account, create one.

Create a new repository called `obsidian-agent-project` or whatever you named your folder.

Copy the `git@github.com:<your_username>/obsidian-agent-project.git` URL.

In your terminal, run the following commands:

```bash
git remote add origin git@github.com:<your_username>/obsidian-agent-project.git
```

Let's create a new branch for main:

```bash
git branch -M main
```

Then let's add the files to the branch:

```bash
git add .
```

Then let's commit the files:

```bash
git commit -m "initial commit"
```

Then let's push the main branch to GitHub:

```bash
git push -u origin main
```

Go to GitHub and check that the files are there.

## Set Up Project Dependencies

Now that we have confirmed that the project is set up correctly, we can start working on the project.

First we want to set up some basic scaffolding and the tools and dependencies we will need initially.

### Ruff: Automated Feedback Loop

We're setting up Ruff as our linter and formatter. When working with AI agents, the goal is to create a feedback loop where the agent can self-correct automatically. Ruff becomes the agent's guardrails—it generates code, receives automatic feedback, and iterates until clean.

Install Ruff as a dev dependency:

```bash
uv add --dev ruff
```

To the `pyproject.toml` we add this configuration:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
exclude = [".git", ".venv", "venv", "__pycache__", ".mypy_cache"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort (import sorting)
    "B",      # flake8-bugbear
    "S",      # flake8-bandit (security)
    "ANN",    # flake8-annotations (type hints)
]

ignore = [
    "ANN101", # Type annotation for self
    "ANN102", # Type annotation for cls
    "S311",   # Standard random is fine for non-crypto
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ANN"]
"__init__.py" = ["F401"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

But we don't add this manually, do we?

No, of course not. We use AI to do it.

Let's copy over this article to our codebase and create a new folder in our directory called `.agents/external-docs`.

This is where we can store any external documents that the AI agent may need to access. This is an example of bringing in context from outside of the project.

Before we use this document, let's add our external-docs folder to `.gitignore` and make another commit.

But wait, we are now committing for the second time in a short amount of time. It's probably time to create a slash command for that.

Let's draft one up:

```
Create a new commit for all of our uncommitted changes
run git status && git diff HEAD && git status --porcelain to see what files are uncommitted
add the untracked and changed files

Add an atomic commit message with an appropriate message

add a tag such as "feat", "fix", "docs", etc. that reflects our work

```

Let's send this as a prompt and make sure it works as we intend to.

Great, it worked!

Let's add it as a slash command so we don't have to write it again next time.

We need to create a `.claude/commands` folder if it doesn't exist, then add a new command file called `commit.md`.

Now we want to commit our command as well, so let's try the command by committing the command itself.

We need to reload Claude Code to load in our new command. Let's do that.

Now let's commit with `/commit`.

Perfect! Now let's move on with our Ruff setup.

Let's take the article we added and use it as context to set up Ruff for our project.

We simply write a prompt like this (but first let's clear our context with `/clear`):

```
Using the official Ruff documentation as context, let's set up Ruff for our project optimized for AI self-correction.

Documentation to read: FETCH:(https://docs.astral.sh/ruff/configuration/)
Read and understand the configuration options before continuing.

Don't set up anything beyond Ruff.

Write a simple Python script in main.py then test our Ruff setup when done.
```

Perfect! As we can see in our agent conversation, Claude Code properly tested the setup and corrected any mistakes that were caught by the linter. That is exactly why we need it in the first place.

Now let's move on to MyPy

### MyPy: Type Safety for AI Agents

Type annotations give AI agents clear contracts and prevent hallucinations. Strict typing ensures the agent knows exactly what each function expects and returns.

Install MyPy:

```bash
uv add --dev mypy
```

Add to `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
show_error_codes = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

Let's use AI to set this up. We write a prompt like this:

```
Using the official MyPy documentation as context, set up MyPy for our project.

Documentation to read: FETCH:(https://mypy.readthedocs.io/en/stable/config_file.html)
Read and understand the configuration options, especially strict mode settings.

First, run:
uv add --dev mypy

Then add the MyPy configuration to pyproject.toml based on the documentation, optimized for ai coding.

When you have added the rules, modify main.py to properly test that all of our type checking rules are working as expected.

main.py is just for testing, so feel free to override anything that's there.

When done, write a short summary of what was configured and tested.
```

Perfect, lets commit again /commit

### Pyright: Second Layer Type Checking

MyPy is excellent for pragmatic development, but Pyright catches edge cases that slip through. Pyright enforces structural subtyping more strictly and prevents runtime type errors that MyPy lets slide.

Install Pyright:

```bash
uv add --dev pyright
```

Add to `pyproject.toml`:

```toml
[tool.pyright]
include = ["app"]
exclude = ["**/__pycache__", ".venv", ".mypy_cache"]

pythonVersion = "3.12"
typeCheckingMode = "strict"

reportMissingImports = true
reportUnusedImport = true
reportUnusedVariable = true
reportOptionalMemberAccess = true
reportUnknownParameterType = true
reportUnknownArgumentType = true
reportUnknownVariableType = true
```

Let's use AI to set this up. We write a prompt like this:

```
Using the official Pyright documentation as context, set up Pyright for our project as a second layer of type safety.

Documentation to read: FETCH:(https://github.com/microsoft/pyright/blob/main/docs/configuration.md)
Read and understand the configuration options, especially type checking modes and diagnostic rules.

First, run:
uv add --dev pyright

Then add the Pyright configuration to pyproject.toml based on the documentation. Use strict mode with all safety checks enabled.

When you have added the rules, run both MyPy and Pyright on main.py to verify both type checkers pass.

main.py is just for testing, so feel free to override anything that's there.

When done, write a short summary comparing what Pyright caught vs MyPy.
```

Perfect, lets commit again /commit

### Pytest: Testing Infrastructure

Tests are non-negotiable, and AI removes all excuses not to write them. Test generation is fast with AI—let it generate test structure, but always validate assertions yourself.

Install pytest:

```bash
uv add --dev pytest pytest-cov
```

Tests will live next to the code they test (e.g., `test_service.py` next to `service.py`).

Let's use AI to set this up. We write a prompt like this:

```
Using the official pytest-asyncio documentation as context, set up pytest for our project.

Documentation to read: FETCH:(https://pytest-asyncio.readthedocs.io/)
Read and understand async test setup, fixtures, and event loop configuration.

First, run:
uv add --dev pytest pytest-cov pytest-asyncio

Then create tests for main.py following best practices from the documentation.

Make sure all tests pass, and that Ruff, MyPy, and Pyright checks all pass as well.

When everything is green, run /commit to commit the changes.

Write a short summary of what was configured and tested.
output:
Summary: [short descriptive summary]
Files changed: [bullet list]
# tests passing: [bullet list]
exact commit message used:
```

Perfect, now next prompt before we continue:
"
before we continue, please add .coverage, .mypy_cache, .ruff_cache, .pytest_cache, and .pyright to gitignore
"

### Structured Logging

Structured logging makes debugging grep-able and consistent. AI agents need clear patterns to follow when adding observability.

Install structlog:

```bash
uv add structlog
```

We'll use this pattern throughout the project (hybrid dotted namespace):

```python
import structlog

logger = structlog.get_logger()

# Format: {domain}.{component}.{action}_{state}
logger.info(
    "user.registration_started",
    email=email,
    source="api"
)

logger.info(
    "user.registration_completed",
    user_id=user.id,
    email=email
)
```

Let's use AI to set this up. We write a prompt like this:

```
Using this article as context, set up structured logging for our project.

Here is the article to read: .agents/external-docs/ai-coding-project-setup-guide.md
The file contains the hybrid logging pattern we need to implement.

First, run:
uv add structlog

Then create app/core/logging.py with:
- JSON output for AI-parseable logs
- Request ID correlation using context variables
- Hybrid dotted namespace pattern: domain.component.action_state
  - Format: {domain}.{component}.{action}_{state}
  - Examples: user.registration_started, database.connection_initialized
  - States: _started, _completed, _failed, _validated, _rejected
- Exception formatting with exc_info for stack traces
- See .agents/external-docs/ai-coding-project-setup-guide.md section 6 for pattern details

Create a simple example in app/main.py demonstrating the logging pattern.

Write unit tests in app/core/tests/test_logging.py

Ruff linting, MyPy, and Pyright must all pass with no errors. You can see the setup in pyproject.toml

When everything is green run /commit

When done, write a short summary of what was configured and how to use it.
output:
Summary: [short descriptive summary]
Key features: [bullet list of logging capabilities]
Usage example: [show the basic pattern]
```

## Containerization with Docker

Docker ensures consistent environments across development and production. Using uv's official Docker images provides optimized, reproducible builds with proper caching.

### Docker Setup

We'll use a multi-stage build to optimize image size and build times. The official uv Docker images include uv pre-installed and optimized for production use.

Create a `Dockerfile` in the project root:

```dockerfile
# Build stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Install dependencies (separate layer for caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy project and install
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy only the virtual environment
COPY --from=builder /app/.venv /app/.venv

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create a `.dockerignore` file:

```
.venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
.pyright
.coverage
.git
.env
```

Let's use AI to set this up. We write a prompt like this:

```
Using this article as context, set up Docker for our project with uv.

Here is the article to read FETCH:(https://docs.astral.sh/uv/guides/integration/docker/)
read it and fully understand it before you continue, do any additional research as needed

Create:
1. Dockerfile using multi-stage build with official uv images
   - Use python3.12-bookworm-slim as base
   - Separate dependency installation layer for caching
   - Use --no-editable for production builds
   - Include cache mounts for uv

2. .dockerignore file to exclude:
   - Virtual environments (.venv)
   - Cache directories (.mypy_cache, .ruff_cache, .pytest_cache, .pyright)
   - Python bytecode (__pycache__, *.pyc)
   - Git and environment files

3. docker-compose.yml for local development with:
   - Volume mounts for the project (excluding .venv)
   - Port mapping (8123:8123)
   - Environment variable support

Test the setup:
- Build the Docker image successfully
- Verify the image size is reasonable
- Test running the container

When done, write a short summary of the Docker setup.
output:
Summary: [short descriptive summary]
Image details: [size, base image, key optimizations]
Usage commands: [docker build, docker run, docker compose]
```

Lets test all of this manually

now:

perfect, now before we continue lets clean up files we dont need.

git rm main.py && git rm test_main.py

## FastAPI Foundation with Pydantic Settings

Now lets setup fastapi for our project

FastAPI provides a modern, fast async web framework with automatic API documentation. Combined with Pydantic's strict type validation, we get runtime safety and excellent AI agent integration.

We will use this to connect to the openai compatible api from the obsidian copilot.

**Why FastAPI + Pydantic:**

- Native async/await support for database operations
- Automatic OpenAPI documentation (Swagger UI at /docs)
- Type hints throughout = AI-friendly (agents understand contracts)
- Pydantic validates data at runtime, preventing invalid states
- Settings management via pydantic-settings (12-factor app pattern)

**Project Structure Overview:**

```
app/
├── core/               # Infrastructure (foundation before features)
│   ├── __init__.py
│   ├── config.py      # Settings with pydantic-settings
│   ├── logging.py     # Already exists (structured logging)
│   ├── middleware.py  # Request logging, CORS
└── main.py            # FastAPI application
```

### FastAPI + Configuration + Middleware

We'll set up the FastAPI application with proper configuration management and middleware that integrates with our existing structured logging.

Let's use AI to set this up. We write a prompt like this:

````
Using the vertical slice architecture guide as context, set up FastAPI with Pydantic for our project.

Context articles to read:
1. .agents/external-docs/vertical-slice-architecture-setup-guide.md
   Read the article to understand infrastructure patterns.

2. FastAPI best practices: FETCH:(https://fastapi.tiangolo.com/advanced/events/)
   Focus on lifespan events for startup/shutdown

First, install dependencies:
uv add fastapi uvicorn[standard] pydantic-settings python-dotenv

Then create these files:

1. app/core/config.py with:
   - Settings class using pydantic-settings BaseSettings
   - Fields: app_name, version, environment, log_level, api_prefix
   - CORS settings: allowed_origins (list)
   - All fields properly typed with descriptions
   - Cached get_settings() function using @lru_cache
   - Settings loaded from .env file (with required=False since it won't exist yet)
   - Example:
     ```python
     class Settings(BaseSettings):
         model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

         app_name: str = "Obsidian Agent Project"
         version: str = "0.1.0"
         environment: str = "development"
         log_level: str = "INFO"
         api_prefix: str = "/api"

         # CORS
         allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8123"]
     ```

2. app/core/middleware.py with:
   - RequestLoggingMiddleware that integrates with our existing app.core.logging
   - Sets request_id from X-Request-ID header or generates new one using set_request_id()
   - Logs "request.started" with method, path, client_host
   - Logs "request.completed" with method, path, status_code, duration_seconds
   - Logs "request.failed" with exc_info=True on exceptions
   - Adds X-Request-ID to response headers
   - setup_middleware(app) function that adds RequestLoggingMiddleware and CORS
   - Use settings.allowed_origins for CORS

3. Update app/main.py to be a FastAPI application:
  - Clean up existing example code for logging
   - Import FastAPI, setup_middleware, setup_logging, get_settings, get_logger
   - Create lifespan async context manager that:
     - Calls setup_logging(log_level=settings.log_level) on startup
     - Gets logger and logs "application.startup" with environment
     - Yields
     - Logs "application.shutdown" on shutdown
   - Create FastAPI app with lifespan, title, version from settings
   - Call setup_middleware(app)
   - Add root endpoint GET / that returns:
     {
       "message": "Obsidian Agent Project",
       "version": settings.version,
       "docs": "/docs"
     }
   - Add if __name__ == "__main__": block that runs uvicorn on port 8123

4. Create .env.example with:
   - Application settings only (no database yet - we'll add that next)
   - Clear comments explaining each setting
   - Example content:
     ```
     # =============================================================================
     # Application Configuration
     # =============================================================================

     # Application
     APP_NAME=Obsidian Agent Project
     VERSION=0.1.0
     ENVIRONMENT=development
     LOG_LEVEL=INFO
     API_PREFIX=/api

     # CORS - allowed origins for cross-origin requests
     ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8123
     ```

5. Update pyproject.toml:
   - Change name to "VSA fastapi project"
   - Add proper description: "FastAPI + PostgreSQL starter with vertical slice architecture, optimized for AI coding"
   - Update known-first-party in ruff config: ["app"]

6. Create test files:

   app/core/tests/test_config.py:
   - Test Settings instantiation with defaults
   - Test Settings from environment variables
   - Test get_settings() caching works
   - Test allowed_origins parsing (list from string)

   app/core/tests/test_middleware.py:
   - Test RequestLoggingMiddleware generates request_id
   - Test middleware uses X-Request-ID header if provided
   - Test middleware logs request.started and request.completed
   - Test middleware logs request.failed with exc_info on exceptions
   - Test X-Request-ID appears in response headers
   - Use pytest fixtures with mock logger to verify log calls

   app/tests/test_main.py:
   - Test root endpoint returns correct JSON structure
   - Test /docs endpoint is accessible
   - Test lifespan events (startup logging)
   - Test CORS headers are present
   - Use httpx.AsyncClient for testing FastAPI endpoints
   - Mock settings if needed for consistent tests

Test requirements:

e2e testing:
- Start the app: uv run uvicorn app.main:app --reload --port 8123
- curl http://localhost:8123 and verify root endpoint returns correct JSON
- curl http://localhost:8123/docs and verify Swagger UI appears
- Check terminal logs - should see structured JSON logs with request_id
- Send request with curl -H "X-Request-ID: test-123" http://localhost:8123
  and verify logs include request_id: "test-123"

Automated testing:
- Run all tests: pytest -v
- Verify test coverage for new modules: pytest --cov=app.core --cov-report=term-missing
- All tests should pass (logging tests, config tests, middleware tests, API tests)
- All linting (ruff check .), type checking (mypy app/, pyright app/) must pass

Expected test output:
- test_config.py: ~4 tests passing (settings, defaults, caching)
- test_middleware.py: ~5 tests passing (request_id, logging, headers)
- test_main.py: ~4 tests passing (root endpoint, docs, CORS)
- Total: ~13+ tests passing
- Coverage: >80% for app/core modules

When everything is green, let the user know we are ready to commit

Output format:
Summary: [short summary of what was built]
Files created: [bullet list]
Configuration: [key settings explained]
Test results: [manual testing + linting + type checking]
````

Lets commit this work after we manually test start the server and test the endpoints.

Now something we commonly see when we use linters and type checkers with AI is that they might add ignore comments and ignore certain warnings, we want to make sure they didn't ignore something we actually want to have checked.

lets create a follow up prompt here before we move on to the next section.

Prompt
´´´
Find all noqa/type:ignore comments in the codebase, investigate why they exist, and provide recommendations for resolution or justification.

Create a markdown report file (create the reports directory if not created yet): `.agents/reports/ignore-comments-report-{YYYY-MM-DD}.md`
report:

**Why it exists:**
{explanation of why the suppression was added}

**Options to resolve:**

1. {Option 1: description}
   - Effort: {Low/Medium/High}
   - Breaking: {Yes/No}
   - Impact: {description}

2. {Option 2: description}
   - Effort: {Low/Medium/High}
   - Breaking: {Yes/No}
   - Impact: {description}

**Tradeoffs:**

- {Tradeoff 1}
- {Tradeoff 2}

**Recommendation:** {Remove | Keep | Refactor}
{Justification for recommendation}

---

{Repeat for each comment}
´´´

Now let's look over the report and see which ones we want to address now and which ones we can leave for later.

now you can decide if you want to commit or ignore your report directory, i like to ignore it becuase i generate a lot of reports.

Now we can save this as a slashcommand!

lets commit again

Perfect! We now have a FastAPI application with proper configuration and request logging.

since we made changes here lets revalidate with another prompt

´´´

Run comprehensive validation of the project to ensure all tests, type checks, linting, and deployments are working correctly.

Execute the following commands in sequence and report results:

## 1. Test Suite

```bash
uv run pytest -v
```

**Expected:** All tests pass (currently 34 tests), execution time < 1 second

## 2. Type Checking

```bash
uv run mypy app/
```

**Expected:** "Success: no issues found in X source files"

```bash
uv run pyright app/
```

**Expected:** "0 errors, 0 warnings, 0 informations"

## 3. Linting

```bash
uv run ruff check .
```

**Expected:** "All checks passed!"

## 4. Local Server Validation

Start the server in background:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8123 &
```

Wait 3 seconds for startup, then test endpoints:

```bash
curl -s http://localhost:8123/ | python3 -m json.tool
```

**Expected:** JSON response with app name, version, and docs link

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8123/docs
```

**Expected:** HTTP Status: 200

```bash
curl -s -i http://localhost:8123/ | head -10
```

**Expected:** Headers include `x-request-id` and status 200

Stop the server:

```bash
lsof -ti:8123 | xargs kill -9 2>/dev/null || true
```

## 5. Docker Deployment Validation

Build and start Docker service:

```bash
docker-compose up -d --build
```

**Expected:** Container builds successfully and starts

Wait 5 seconds, then verify container status:

```bash
docker-compose ps
```

**Expected:** Container status shows "Up"

Test Docker endpoints:

```bash
curl -s http://localhost:8123/ | python3 -m json.tool
```

**Expected:** Same JSON response as local server

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8123/docs
```

**Expected:** HTTP Status: 200

Check Docker logs:

```bash
docker-compose logs app | tail -20
```

**Expected:** Structured JSON logs with request_id, startup message, request logging

Stop Docker service:

```bash
docker-compose down
```

## 6. Summary Report

After all validations complete, provide a summary report with:

- Total tests passed/failed
- Type checking status (mypy + pyright)
- Linting status
- Local server status
- Docker deployment status
- Any errors or warnings encountered
- Overall health assessment (PASS/FAIL)

**Format the report clearly with sections and status indicators (✅/❌)**
´´´

Let's save this as another / command in our .claude/commands directory

Before moving to database setup, let's verify manually as well:

- Run the server
- `/` returns project info
- `/docs` shows Swagger UI
- Logs show structured JSON with request IDs
- All type checkers pass

## Database Infrastructure

Now we'll add PostgreSQL support with async SQLAlchemy, health checks, error handling, and Alembic migrations.

**What we're building:**

- Provider-agnostic database setup (works with Docker, Supabase, Neon, Railway, etc.)
- Health check endpoints for monitoring
- Global exception handling
- Migration system with Alembic
- Test infrastructure for async database operations

### Database + Health Checks + Error Handling

Let's use AI to set this up:

````
Using the vertical slice architecture guide, set up PostgreSQL database infrastructure.

Context: READ .agents/external-docs/vertical-slice-architecture-setup-guide.md

This setup must be provider-agnostic - work with ANY PostgreSQL provider (Docker, Supabase, Neon, Railway, etc.)

First, install dependencies:
uv add sqlalchemy[asyncio] asyncpg alembic
uv add --dev pytest-asyncio httpx (if not already added)

Then create these NEW files:

1. app/core/database.py with:
   - Import create_async_engine, AsyncSession, async_sessionmaker from sqlalchemy.ext.asyncio
   - Import DeclarativeBase from sqlalchemy.orm
   - Get settings from core.config
   - Create async engine with:
     * settings.database_url
     * pool_pre_ping=True (test connections before using)
     * pool_size=5, max_overflow=10
     * echo=True if environment is "development" else False
   - Create AsyncSessionLocal using async_sessionmaker
   - Define Base class extending DeclarativeBase (for SQLAlchemy models)
   - Define async get_db() generator:
     ```python
     async def get_db() -> AsyncGenerator[AsyncSession, None]:
         async with AsyncSessionLocal() as session:
             try:
                 yield session
             finally:
                 await session.close()
     ```

2. app/core/exceptions.py (NEW file) with:
   - Custom exception classes:
     * DatabaseError(Exception) - base database exception
     * NotFoundError(DatabaseError) - resource not found
     * ValidationError(DatabaseError) - validation failed
   - Global exception handler for FastAPI:
     * async def database_exception_handler that logs errors and returns JSON
     * Returns {"error": str(exc), "type": type(exc).__name__}
   - Function to register handlers: setup_exception_handlers(app)

3. app/core/health.py (NEW file) with:
   - Import APIRouter, Depends, HTTPException from fastapi
   - Import AsyncSession and get_db from core.database
   - Import get_logger from core.logging
   - Import text from sqlalchemy
   - Create router = APIRouter(tags=["health"])
   - Three endpoints (NO prefix - health checks are typically at root):

     GET /health:
     - No dependencies
     - Returns {"status": "healthy", "service": "api"}

     GET /health/db:
     - Uses Depends(get_db)
     - Executes SELECT 1 via db.execute(text("SELECT 1"))
     - Returns {"status": "healthy", "service": "database", "provider": "postgresql"}
     - Logs errors with logger.error("database.health_check_failed", exc_info=True)
     - Raises HTTPException(503) if database fails

     GET /health/ready:
     - Uses Depends(get_db) and get_settings
     - Checks database connection
     - Returns {"status": "ready", "environment": settings.environment, "database": "connected"}
     - Raises HTTPException(503) if not ready

4. UPDATE existing app/core/config.py:
   - Add database_url field to Settings class:
     ```python
     # Database
     database_url: str
     ```

5. UPDATE existing app/main.py:
   - Import health router, database exception handlers, engine
   - Update lifespan to:
     * On startup: Log "database.connection.initialized"
     * On shutdown: Call await engine.dispose() and log "database.connection.closed"
   - Add app.include_router(health_router) (no prefix!)
   - Call setup_exception_handlers(app)

6. UPDATE existing docker-compose.yml to add PostgreSQL service:
   - Add db service using postgres:18-alpine image
   - Environment variables: POSTGRES_USER=postgres, POSTGRES_PASSWORD=postgres, POSTGRES_DB=obsidian_db
   - Port mapping: 5433:5432 (host:container - use non-standard port to avoid conflicts with local PostgreSQL)
   - Named volume: postgres_data for persistence
   - Health check: pg_isready -U postgres (interval: 5s, timeout: 5s, retries: 5)
   - App service changes:
     * Add depends_on with db service and condition: service_healthy
     * Override DATABASE_URL for Docker networking: postgresql+asyncpg://postgres:postgres@db:5432/obsidian_db
   - Add volumes section at bottom: postgres_data: {}
   - Note: Port 5433 on host avoids conflicts with any local PostgreSQL on standard port 5432

7. Initialize Alembic for migrations:
   - Run: alembic init alembic
   - Edit alembic/env.py to use async:
     * Import asyncio
     * Import Base from app.core.database
     * Import settings from app.core.config
     * Set target_metadata = Base.metadata
     * Set sqlalchemy.url from settings.database_url in config section
     * Convert run_migrations_online to async function
     * Use create_async_engine and AsyncConnection
   - Edit alembic.ini:
     * Comment out sqlalchemy.url line (we get it from settings)

8. UPDATE existing .env.example to add database section:
   - Add comprehensive database examples with comments:
     ```
     # =============================================================================
     # Database Configuration
     # =============================================================================
     # Works with ANY PostgreSQL provider - just change the connection string

     # Docker (default - use with docker-compose up)
     # Note: Using port 5433 to avoid conflicts with local PostgreSQL on standard port 5432
     DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db

     # Supabase Cloud
     # DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres

     # Supabase Local (default configuration)
     # Start with: supabase start
     # DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres

     # Neon (Serverless Postgres)
     # DATABASE_URL=postgresql+asyncpg://[user]:[password]@[endpoint].neon.tech/[dbname]?sslmode=require

     # Railway
     # DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host].railway.app:[port]/railway

     # Local PostgreSQL (non-Docker, standard port)
     # If you have PostgreSQL installed locally on the standard port:
     # DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/obsidian_db

     # Local PostgreSQL (non-Docker, custom port)
     # If you installed PostgreSQL on a custom port to avoid conflicts:
     # DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db
     ```

9. Create .env file for local development (gitignored):
   - Copy from .env.example
   - Use Docker connection string with port 5433
   - Set LOG_LEVEL=DEBUG for development
   - DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/obsidian_db

10. Update .gitignore:
   - Add .env (actual secrets)
   - Ensure alembic/versions/__pycache__ is ignored

11. Create test fixtures and test files:

   **CRITICAL: Test Fixtures for Event Loop Isolation**

   app/tests/conftest.py (NEW - REQUIRED):
   - Create test-scoped fixtures to avoid event loop conflicts
   - The module-level engine in database.py is bound to the first event loop
   - pytest-asyncio creates a new event loop per test (proper isolation)
   - Fixtures ensure each test gets an engine bound to its own event loop

   ```python
   """Pytest fixtures for integration tests.

   IMPORTANT: Integration tests MUST use these fixtures instead of
   importing AsyncSessionLocal/engine from app.core.database directly.

   Why? The module-level engine in database.py is bound to the first
   event loop. pytest-asyncio creates new loops per test. Using fixtures
   ensures each test gets an engine bound to its own loop, avoiding
   "Future attached to different loop" errors.
   """
   import pytest
   from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
   from app.core.config import get_settings

   @pytest.fixture(scope="function")
   async def test_db_engine():
       """Create fresh database engine for each test."""
       settings = get_settings()
       engine = create_async_engine(
           settings.database_url,
           pool_pre_ping=True,
           pool_size=5,
           max_overflow=10,
           echo=False,  # Quiet in tests
       )
       yield engine
       await engine.dispose()

   @pytest.fixture(scope="function")
   async def test_db_session(test_db_engine):
       """Create fresh database session for each test."""
       async_session = async_sessionmaker(
           test_db_engine,
           class_=AsyncSession,
           expire_on_commit=False,
           autocommit=False,
           autoflush=False,
       )
       async with async_session() as session:
           yield session
   ```

   app/core/tests/test_database.py:
   - Test async engine creation
   - Test get_db() session lifecycle (creates and closes)
   - Test Base class is properly configured
   - Use pytest-asyncio for async tests
   - Mock settings.database_url for isolated testing

   app/core/tests/test_exceptions.py:
   - Test DatabaseError, NotFoundError, ValidationError raise correctly
   - Test exception handler returns proper JSON structure
   - Test exception handler logs with exc_info
   - Verify error response format matches expectations

   app/core/tests/test_health.py:
   - Test GET /health returns 200 without database
   - Test GET /health/db returns 200 with database connected
   - Test GET /health/db returns 503 when database fails
   - Test GET /health/ready returns 200 when all dependencies healthy
   - Use pytest fixtures to override get_db dependency
   - Mock database failures to test error paths

   Integration tests:
   app/tests/test_database_integration.py:
   - **MUST use test_db_session fixture parameter, NOT module imports**
   - Example test structure:
     ```python
     @pytest.mark.asyncio
     async def test_database_connection(test_db_session):
         """Test using FIXTURE, not module import."""
         result = await test_db_session.execute(text("SELECT 1"))
         value = result.scalar_one()
         assert value == 1
     ```
   - Test full database connection with real PostgreSQL
   - Test session lifecycle, metadata operations
   - Test transaction rollback behavior
   - Test connection pool management
   - Test connection recovery after errors
   - These tests require docker-compose up db to be running
   - Use pytest markers: @pytest.mark.integration
   - Can be skipped in CI if no database available
   - ALL integration tests MUST accept test_db_session or test_db_engine as parameters

Test requirements:

testing (with Docker):
- Start Docker services: docker-compose up -d
- Wait for services to be healthy: docker-compose ps
- Test health endpoints:
  * curl http://localhost:8123/health (should return 200)
  * curl http://localhost:8123/health/db (should return 200 with database status)
  * curl http://localhost:8123/health/ready (should return 200)
- Test /docs endpoint - verify health endpoints appear
- Run alembic check (should succeed with no errors)
- Create test migration: alembic revision -m "initial" (should create file)
- Run migration: alembic upgrade head (should succeed)
- Check database: docker-compose exec db psql -U postgres -d obsidian_db -c "\dt"
  (should show alembic_version table)

unit testing:
Unit tests (no database required):
- Run unit tests: pytest -v -m "not integration"
- These test business logic without real database connections
- Tests should pass without docker-compose running

Integration tests (database required):
- Ensure Docker database is running: docker-compose up -d db
- Run integration tests: pytest -v -m integration
- These test actual database connectivity
- Verify health endpoints work with real PostgreSQL

Full test suite:
- Run all tests: pytest -v
- Verify test coverage: pytest --cov=app --cov-report=term-missing
- All linting (ruff check ., mypy app/, pyright app/) must pass

Expected test output:
- test_database.py: ~3 tests passing (engine, session, Base)
- test_exceptions.py: ~4 tests passing (custom exceptions, handlers)
- test_health.py: ~6 tests passing (health endpoints, error cases)
- test_database_integration.py: ~3 tests passing (real DB connection)
- Total from Step 1: ~13 tests
- Total from Step 2: ~16 tests
- Grand total: ~29+ tests passing
- Coverage: >80% for app/core modules

Configure pytest markers in pyproject.toml:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Creates new event loop per test (proper isolation)
testpaths = ["app", "tests"]
markers = [
    "integration: marks tests requiring real database (deselect with '-m \"not integration\"')",
]
```

**Important:** asyncio_mode = "auto" creates a fresh event loop for each test.
This is why integration tests MUST use fixtures (test_db_engine, test_db_session)
instead of importing the module-level engine from database.py. The module-level
engine is correct for production (one loop), but tests need per-test fixtures.

Stop services when done: docker-compose down

When everything is green, let the user know we are ready to commit

Output format:
Summary: [comprehensive summary of database infrastructure]
Files created/modified: [bullet list with descriptions]
Database features: [provider-agnostic, health checks, migrations, etc.]
Docker setup: [postgres service details]
Test results: [health endpoints, migrations, linting, type checking]
````

Perfect! We now have a complete database infrastructure that works with any PostgreSQL provider.

Let's verify:

- Docker Compose starts PostgreSQL successfully
- Health endpoints return 200 OK
- Alembic migrations work
- Type checkers pass

Thats great but we dont have to verify manually, lets use the /validate command

Lets commit here with the /commit command

We can also see that we had some ignore patterns added

lets run the /check-ingore-comments.md command as well and decide if we want to address any of these

If you addressed anything, lets run /validate again before we /commit

## Shared Infrastructure

Before building features, we need shared utilities to prevent code duplication. Every model needs timestamps. Every list endpoint needs pagination. Let's set these up once.

**Why this matters:**

- Prevents duplication across features
- Establishes consistent patterns
- Makes AI-generated code more uniform
- Follows the "extract when used by 3+ features" rule preemptively for universals

### Shared Utilities & Patterns

Let's use AI to set this up:

```
Create shared infrastructure for cross-feature utilities.

Context: READ .agents/external-docs/vertical-slice-architecture-setup-guide.md

We're setting up utilities that ALL features will use:
- Database model mixins (timestamps on every table)
- API patterns (pagination on every list endpoint)
- Common response formats (consistent error/success responses)
- Utility functions (date handling, validation)

Create these files:

1. app/shared/__init__.py (empty file for package)

2. app/shared/models.py with:
   - TimestampMixin class with:
     * created_at: DateTime column with default=datetime.utcnow
     * updated_at: DateTime column with default=datetime.utcnow, onupdate=datetime.utcnow
     * Use @declared_attr for columns (SQLAlchemy mixin pattern)
   - Proper imports from sqlalchemy
   - All future models will inherit this mixin

3. app/shared/schemas.py with:
   - PaginationParams(BaseModel):
     * page: int = Field(default=1, ge=1, description="Page number")
     * page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
     * Property: offset (calculated as (page - 1) * page_size)

   - PaginatedResponse(BaseModel, Generic[T]):
     * items: List[T]
     * total: int
     * page: int
     * page_size: int
     * total_pages: int (calculated from total/page_size, rounded up)
     * Use Generic[T] for type-safe responses

   - ErrorResponse(BaseModel):
     * error: str
     * type: str
     * detail: str | None = None
     * Used by exception handlers

4. app/shared/utils.py with:
   - utcnow() -> datetime:
     * Returns datetime.now(timezone.utc)
     * Consistent timezone-aware timestamps
   - format_iso(dt: datetime) -> str:
     * Returns dt.isoformat()
     * Standard ISO 8601 formatting

5. Create comprehensive tests:

   app/shared/tests/__init__.py (empty)

   app/shared/tests/test_models.py:
   - Test TimestampMixin creates columns correctly
   - Test timestamps are set on model creation
   - Use a test model class that inherits the mixin
   - Verify created_at and updated_at are populated

   app/shared/tests/test_schemas.py:
   - Test PaginationParams defaults (page=1, page_size=20)
   - Test PaginationParams validation (page >= 1, page_size 1-100)
   - Test PaginationParams.offset calculation
   - Test PaginatedResponse structure with mock data
   - Test PaginatedResponse total_pages calculation
   - Test ErrorResponse structure

   app/shared/tests/test_utils.py:
   - Test utcnow() returns timezone-aware datetime
   - Test format_iso() returns ISO 8601 string
   - Test date utility functions

Test requirements:

Unit tests (no database needed):
- Run tests: pytest app/shared/tests/ -v
- All schema validation tests should pass
- All utility function tests should pass

Integration tests (with database):
- Test TimestampMixin with real SQLAlchemy model
- Verify timestamps are persisted to database
- Mark with @pytest.mark.integration

Expected test results:
- test_models.py: ~3 tests (mixin, columns, auto-population)
- test_schemas.py: ~6 tests (pagination, validation, calculations)
- test_utils.py: ~2 tests (timezone, formatting)
- Total: ~11 new tests
- All tests passing
- All linting (ruff, mypy, pyright) must pass

When everything is green, let the user know we are ready to commit and all validations pass

Output format:
Summary: [shared infrastructure created]
Files created: [list with descriptions]
Patterns established: [pagination, timestamps, utilities]
Test results: [test counts and coverage]
Usage examples: [how to use TimestampMixin, PaginationParams]
```

Perfect! Now we have reusable infrastructure that prevents duplication.

Let's verify what we created:

- TimestampMixin: Every model gets created_at/updated_at automatically
- PaginationParams: Every list endpoint uses consistent pagination
- PaginatedResponse: Every list response has the same structure
- ErrorResponse: Consistent error format across all endpoints

lets validate /validate

## Project Complete!

You now have a production-ready FastAPI + PostgreSQL starter with:

✅ **Vertical Slice Architecture** - Core infrastructure separated from features
✅ **Type Safety** - Ruff + MyPy + Pyright in strict mode
✅ **Structured Logging** - JSON logs with request correlation
✅ **Testing** - pytest with async support
✅ **Database** - Provider-agnostic PostgreSQL (Docker, Supabase, Neon, Railway)
✅ **Migrations** - Alembic with async support
✅ **Health Checks** - /health, /health/db, /health/ready
✅ **API Documentation** - Automatic Swagger UI at /docs
✅ **Docker** - Multi-stage build with uv
✅ **AI-Optimized** - Grep-able, typed, structured

**Optional Next Steps:**

- Add authentication (JWT, OAuth)
- Add more feature slices
- Deploy to production (Railway, Fly.io, etc.)
- Add background jobs (Celery, ARQ)
- Add caching (Redis)

This template is now ready to be forked and customized for any API project!