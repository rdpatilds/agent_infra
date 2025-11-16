"""Example Celery tasks demonstrating best practices."""

import logging
from typing import Any

from celery import Task  # type: ignore[import-untyped]

from app.core.celery_utils import get_celery_app

logger = logging.getLogger(__name__)

celery_app = get_celery_app()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes between retries
    retry_jitter=True,  # Add randomness to prevent thundering herd
)
def send_email(self: Task, to: str, subject: str, body: str) -> dict[str, Any]:
    """Send an email asynchronously with retry logic.

    This is an idempotent task that demonstrates Celery best practices:
    - Retry with exponential backoff
    - Comprehensive logging
    - Idempotent operation
    - Type hints for parameters

    Args:
        to: Email recipient address
        subject: Email subject line
        body: Email body content

    Returns:
        dict with status and message details

    Raises:
        MaxRetriesExceededError: If task fails after all retries
    """
    task_id = self.request.id
    logger.info(
        "Starting email task",
        extra={
            "task_id": task_id,
            "to": to,
            "subject": subject,
            "retry_count": self.request.retries,
        },
    )

    try:
        # Simulate email sending logic
        # In production, this would call an email service like SendGrid, AWS SES, etc.
        logger.info(
            "Simulating email send",
            extra={
                "task_id": task_id,
                "to": to,
                "subject": subject,
            },
        )

        # Simulate success
        result = {
            "status": "success",
            "task_id": task_id,
            "to": to,
            "subject": subject,
            "message": "Email sent successfully (simulated)",
        }

        logger.info("Email task completed successfully", extra={"task_id": task_id})
        return result

    except Exception as exc:
        logger.error(
            "Email task failed",
            extra={
                "task_id": task_id,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
            exc_info=True,
        )

        # Let the autoretry_for handle the retry
        # This will automatically retry with exponential backoff
        raise


@celery_app.task(bind=True)
def process_data(self: Task, data: dict[str, Any]) -> dict[str, Any]:
    """Process data asynchronously.

    Example task for data processing workflows.

    Args:
        data: Dictionary of data to process

    Returns:
        dict with processed results
    """
    task_id = self.request.id
    logger.info(
        "Processing data", extra={"task_id": task_id, "data_keys": list(data.keys())}
    )

    # Simulate data processing
    result = {
        "status": "success",
        "task_id": task_id,
        "processed_items": len(data),
        "result": f"Processed {len(data)} items",
    }

    logger.info("Data processing completed", extra={"task_id": task_id})
    return result
