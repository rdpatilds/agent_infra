"""Celery application factory and configuration."""

from celery import Celery  # type: ignore[import-untyped]

from app.core.config import get_settings


def create_celery_app() -> Celery:
    """Create and configure Celery application instance.

    Returns:
        Celery: Configured Celery application instance.
    """
    settings = get_settings()

    celery_app = Celery("agent_infra")

    # Testing configuration
    celery_app.conf.task_always_eager = settings.celery_task_always_eager

    # Configure broker and backend
    # Use cache+memory backend for testing (eager mode)
    if settings.celery_task_always_eager:
        celery_app.conf.broker_url = "memory://"
        celery_app.conf.result_backend = "cache+memory://"
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True
    else:
        celery_app.conf.broker_url = settings.celery_broker_url
        celery_app.conf.result_backend = settings.celery_result_backend

    # Task configuration - best practices from Celery docs
    celery_app.conf.task_acks_late = True  # Acknowledge after task completion
    celery_app.conf.task_reject_on_worker_lost = True  # Reject on worker crash
    celery_app.conf.result_expires = 3600  # Results expire after 1 hour

    # Additional recommended settings
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.timezone = "UTC"
    celery_app.conf.enable_utc = True

    # Autodiscover tasks from app.*.tasks modules
    celery_app.autodiscover_tasks(["app.example"], related_name="tasks", force=True)

    return celery_app
