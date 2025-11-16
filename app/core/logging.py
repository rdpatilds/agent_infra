"""Structured logging configuration with JSON output and request correlation.

This module provides:
- JSON output for AI-parseable logs
- Request ID correlation using context variables
- Hybrid dotted namespace pattern: domain.component.action_state
- Exception formatting with exc_info for stack traces

Logging Pattern:
    Format: {domain}.{component}.{action}_{state}
    Examples:
        - user.registration_started
        - user.registration_completed
        - database.connection_initialized
        - api.request_failed

    States: _started, _completed, _failed, _validated, _rejected

Usage:
    from app.core.logging import get_logger, set_request_id

    logger = get_logger()

    # Set request ID for correlation
    set_request_id("abc-123")

    # Log events
    logger.info("user.registration_started", email=email, source="api")
    logger.info("user.registration_completed", user_id=user.id, email=email)
    logger.error("database.connection_failed", error=str(exc), exc_info=True)
"""

import contextvars
import logging
import sys
import uuid

import structlog
from structlog.typing import EventDict, WrappedLogger

# Context variable for request ID correlation
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


def set_request_id(request_id: str | None = None) -> str:
    """Set the request ID for the current context.

    Generates a new UUID if request_id is not provided.

    Args:
        request_id: Unique identifier for the request (optional)

    Returns:
        The request ID that was set
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    _ = request_id_var.set(request_id)
    return request_id


def get_request_id() -> str:
    """Get the request ID from the current context.

    Returns:
        The current request ID or empty string
    """
    return request_id_var.get()


def add_request_id(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Processor that adds request_id to log events.

    Args:
        logger: The wrapped logger instance
        method_name: The name of the method being called
        event_dict: The event dictionary to process

    Returns:
        Event dictionary with request_id added if available
    """
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging with JSON output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure structlog processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        add_request_id,  # Add request ID from context
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,  # Format exception info
    ]

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Optional logger name. If not provided, uses the caller's module name.

    Returns:
        A bound logger instance
    """
    # structlog.get_logger returns BoundLogger based on our configuration
    return structlog.get_logger(name)  # type: ignore[no-any-return]
