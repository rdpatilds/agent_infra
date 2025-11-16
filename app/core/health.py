"""Health check endpoints for application and dependencies."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

# Router with no prefix - health checks are typically at root level
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint without dependencies.

    Returns:
        dict: Health status of the API service.
    """
    return {"status": "healthy", "service": "api"}


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Database connectivity health check.

    Args:
        db: Database session from dependency injection.

    Returns:
        dict: Health status of the database connection.

    Raises:
        HTTPException: 503 if database connection fails.
    """
    try:
        # Execute simple query to verify database connectivity
        await db.execute(text("SELECT 1"))
        logger.debug("database.health_check.success")
        return {"status": "healthy", "service": "database", "provider": "postgresql"}
    except Exception as e:
        logger.error(
            "database.health_check_failed",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from e


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Readiness check for all application dependencies.

    Verifies that the application is fully ready to handle requests
    by checking all critical dependencies (database, configuration, etc.).

    Args:
        db: Database session from dependency injection.

    Returns:
        dict: Readiness status with environment and dependency info.

    Raises:
        HTTPException: 503 if any dependency is not ready.
    """
    settings = get_settings()

    try:
        # Check database connectivity
        await db.execute(text("SELECT 1"))
        logger.debug("readiness_check.success", environment=settings.environment)

        return {
            "status": "ready",
            "environment": settings.environment,
            "database": "connected",
        }
    except Exception as e:
        logger.error(
            "readiness_check.failed",
            error=str(e),
            environment=settings.environment,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application not ready",
        ) from e
