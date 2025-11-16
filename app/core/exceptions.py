"""Custom exception classes and global exception handlers."""


from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    pass


class NotFoundError(DatabaseError):
    """Exception raised when a requested resource is not found."""

    pass


class ValidationError(DatabaseError):
    """Exception raised when data validation fails."""

    pass


async def database_exception_handler(
    request: Request, exc: DatabaseError
) -> JSONResponse:
    """Global exception handler for database errors.

    Args:
        request: The incoming request that caused the exception.
        exc: The database exception that was raised.

    Returns:
        JSONResponse with error details and appropriate status code.
    """
    logger.error(
        "database.exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        exc_info=True,
    )

    # Determine status code based on exception type
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return JSONResponse(
        status_code=status_code,
        content={"error": str(exc), "type": type(exc).__name__},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers with the FastAPI app.

    Args:
        app: The FastAPI application instance.
    """
    app.add_exception_handler(DatabaseError, database_exception_handler)
    logger.info("exception_handlers.registered", handlers=["DatabaseError"])
