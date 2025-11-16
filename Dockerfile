# Multi-stage Docker build for uv-based Python project
# Base image: python3.13-bookworm-slim (lightweight Debian-based Python)

# Stage 1: Builder - Install dependencies and build the application
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Set environment variables for uv optimization
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
# This allows Docker to cache the dependency layer when only source code changes
COPY pyproject.toml uv.lock ./

# Install dependencies only (without the project itself) using cache mount
# This creates a separate layer that can be cached
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the application source code
COPY . .

# Install the project (now that source code is present) with optimizations:
# - --frozen: Use exact versions from uv.lock without updating
# - --no-editable: Install as a non-editable package (production build)
# - --no-dev: Skip development dependencies
# Cache mount improves build speed for repeated builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --no-dev

# Stage 2: Runtime - Minimal production image
FROM python:3.13-slim-bookworm

# Set runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy only the virtual environment from builder stage
# This excludes source code and build artifacts, keeping the image minimal
COPY --from=builder /app/.venv /app/.venv

# Copy application code (needed for runtime)
COPY --from=builder /app /app

# Expose port 8123 for the application
EXPOSE 8123

# Run FastAPI application with uvicorn
# Bind to 0.0.0.0 to accept connections from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8123"]
