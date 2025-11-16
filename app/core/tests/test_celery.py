"""Tests for Celery configuration and task execution."""

import pytest
from celery import Celery

from app.core.celery import create_celery_app
from app.core.celery_utils import get_celery_app, get_task_result
from app.core.config import get_settings
from app.example.tasks import process_data, send_email


@pytest.fixture
def celery_app() -> Celery:
    """Create a Celery app instance for testing.

    Returns:
        Celery: Configured Celery application instance.
    """
    return create_celery_app()


@pytest.fixture
def celery_eager_mode(monkeypatch):
    """Set Celery to eager mode for synchronous task execution in tests.

    This fixture patches the settings to enable task_always_eager mode,
    which makes tasks execute synchronously in tests.
    """
    # Clear the celery app singleton
    import app.core.celery_utils as celery_utils_module

    celery_utils_module._celery_app = None

    monkeypatch.setenv("CELERY_TASK_ALWAYS_EAGER", "true")
    # Clear the settings cache to pick up the new env var
    get_settings.cache_clear()
    yield
    # Clear again after test to reset
    get_settings.cache_clear()
    celery_utils_module._celery_app = None


def test_celery_app_creation(celery_app):
    """Test that Celery app is created with correct configuration.

    Args:
        celery_app: The Celery app fixture
    """
    assert celery_app is not None
    assert celery_app.main == "agent_infra"

    # Verify configuration
    assert celery_app.conf.task_acks_late is True
    assert celery_app.conf.task_reject_on_worker_lost is True
    assert celery_app.conf.result_expires == 3600
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True


def test_celery_broker_and_backend_config(celery_app):
    """Test that broker and backend are configured correctly.

    Args:
        celery_app: The Celery app fixture
    """
    settings = get_settings()

    # Verify broker and backend are configured
    assert celery_app.conf.broker_url is not None
    assert celery_app.conf.result_backend is not None

    # In production (not eager mode), should use Redis
    if not settings.celery_task_always_eager:
        assert celery_app.conf.broker_url == settings.celery_broker_url
        assert celery_app.conf.result_backend == settings.celery_result_backend
        assert "redis" in celery_app.conf.broker_url.lower()
    else:
        # In eager mode (testing), should use memory backend
        assert celery_app.conf.broker_url == "memory://"
        assert celery_app.conf.result_backend == "cache+memory://"


def test_celery_task_registration(celery_app):
    """Test that tasks are registered correctly.

    Args:
        celery_app: The Celery app fixture
    """
    # Get all registered tasks
    registered_tasks = list(celery_app.tasks.keys())

    # Check that our example tasks are registered
    assert "app.example.tasks.send_email" in registered_tasks
    assert "app.example.tasks.process_data" in registered_tasks


def test_get_celery_app_singleton():
    """Test that get_celery_app returns the same instance."""
    app1 = get_celery_app()
    app2 = get_celery_app()

    assert app1 is app2  # Should be the same instance


def test_send_email_task_eager_execution(celery_eager_mode):
    """Test send_email task executes synchronously using apply().

    Args:
        celery_eager_mode: Fixture that enables eager mode
    """
    # Execute task synchronously without using broker
    result = send_email.apply(
        args=("test@example.com", "Test Email", "This is a test email")
    )

    # Should be available immediately
    assert result.successful()

    # Check result content
    task_result = result.result
    assert task_result["status"] == "success"
    assert task_result["to"] == "test@example.com"
    assert task_result["subject"] == "Test Email"


def test_process_data_task_eager_execution(celery_eager_mode):
    """Test process_data task executes synchronously using apply().

    Args:
        celery_eager_mode: Fixture that enables eager mode
    """
    test_data = {"key1": "value1", "key2": "value2", "key3": "value3"}

    # Execute task synchronously without using broker
    result = process_data.apply(kwargs={"data": test_data})

    # Should be available immediately
    assert result.successful()

    # Check result content
    task_result = result.result
    assert task_result["status"] == "success"
    assert task_result["processed_items"] == 3


def test_get_task_result():
    """Test get_task_result utility function."""
    # Create a dummy task result
    task_id = "test-task-id-12345"

    # Get result object
    result = get_task_result(task_id)

    # Verify it's an AsyncResult object
    from celery.result import AsyncResult  # type: ignore[import-untyped]

    assert isinstance(result, AsyncResult)
    assert result.id == task_id


def test_send_email_task_retry_config():
    """Test that send_email task has correct retry configuration."""
    # Access task configuration
    task = send_email

    assert task.max_retries == 3
    assert task.default_retry_delay == 60
    assert task.autoretry_for == (Exception,)
    assert task.retry_backoff is True
    assert task.retry_backoff_max == 600
    assert task.retry_jitter is True
