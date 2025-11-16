"""Celery utilities and helpers."""

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from celery.result import AsyncResult
else:
    from celery import Task  # type: ignore[import-untyped]
    from celery.result import AsyncResult  # type: ignore[import-untyped]

# Type variable for task return type
T = TypeVar("T")

# Global celery app instance
_celery_app: Any = None


def get_celery_app() -> Any:
    """Get the current Celery application instance.

    Returns:
        Celery: The Celery application instance.

    Raises:
        RuntimeError: If Celery app has not been initialized.
    """
    global _celery_app
    if _celery_app is None:
        from app.core.celery import create_celery_app

        _celery_app = create_celery_app()
    return _celery_app


def get_task_result(task_id: str) -> Any:
    """Get task result by task ID.

    Args:
        task_id: The Celery task ID.

    Returns:
        AsyncResult: The task result object.
    """
    celery_app = get_celery_app()
    return AsyncResult(task_id, app=celery_app)


# Module-level Celery app instance for celery worker command
# This allows using: celery -A app.core.celery_utils worker
app = get_celery_app()


if not TYPE_CHECKING:

    class TypedTask(Task):  # type: ignore[misc,valid-type]
        """Base task class with type hints for better IDE support."""

        pass
