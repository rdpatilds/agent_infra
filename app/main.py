"""FastAPI application with structured logging and vertical slice architecture."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import setup_exception_handlers
from app.core.health import router as health_router
from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events for startup and shutdown.

    Args:
        app: FastAPI application instance

    Yields:
        None: Control back to the application
    """
    # Startup
    setup_logging(log_level=settings.log_level)
    logger = get_logger(__name__)
    logger.info("application.startup", environment=settings.environment)
    logger.info("database.connection.initialized")

    yield

    # Shutdown
    await engine.dispose()
    logger.info("database.connection.closed")
    logger.info("application.shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

# Setup middleware
setup_middleware(app)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health_router)  # No prefix - health checks at root level


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning application information.

    Returns:
        dict: Application name, version, and documentation link
    """
    return {
        "message": "Obsidian Agent Project",
        "version": settings.version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8123)
