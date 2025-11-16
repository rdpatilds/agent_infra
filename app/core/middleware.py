"""Request/response middleware for FastAPI application."""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger, get_request_id, set_request_id

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation ID."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        """Process each request with logging and request ID tracking.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with X-Request-ID header added
        """
        # Extract or generate request ID
        request_id = request.headers.get("X-Request-ID")
        _ = set_request_id(request_id)

        start_time = time.time()
        logger.info(
            "request.started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            logger.info(
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = get_request_id()
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request.failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_seconds=round(duration, 3),
                exc_info=True,
            )
            raise


def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    settings = get_settings()

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
