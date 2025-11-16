"""Unit tests for custom exception classes and handlers."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DatabaseError,
    NotFoundError,
    ValidationError,
    database_exception_handler,
    setup_exception_handlers,
)


def test_database_error_raises():
    """Test that DatabaseError can be raised and caught."""
    with pytest.raises(DatabaseError) as exc_info:
        raise DatabaseError("Test database error")

    assert str(exc_info.value) == "Test database error"


def test_not_found_error_is_database_error():
    """Test that NotFoundError inherits from DatabaseError."""
    with pytest.raises(DatabaseError):
        raise NotFoundError("Resource not found")


def test_validation_error_is_database_error():
    """Test that ValidationError inherits from DatabaseError."""
    with pytest.raises(DatabaseError):
        raise ValidationError("Validation failed")


@pytest.mark.asyncio
async def test_database_exception_handler_returns_json():
    """Test that exception handler returns proper JSON response."""
    # Create mock request
    mock_request = MagicMock()
    mock_request.url.path = "/test/path"

    # Create test exception
    test_error = DatabaseError("Test database error")

    # Call handler
    with patch("app.core.exceptions.logger") as mock_logger:
        response = await database_exception_handler(mock_request, test_error)

    # Verify response
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Verify response content
    assert response.body is not None
    import json

    body = json.loads(response.body)
    assert body["error"] == "Test database error"
    assert body["type"] == "DatabaseError"

    # Verify logging was called with exc_info
    mock_logger.error.assert_called_once()
    call_kwargs = mock_logger.error.call_args[1]
    assert call_kwargs["exc_info"] is True


@pytest.mark.asyncio
async def test_not_found_error_returns_404():
    """Test that NotFoundError returns 404 status code."""
    mock_request = MagicMock()
    mock_request.url.path = "/test/path"

    test_error = NotFoundError("Resource not found")

    with patch("app.core.exceptions.logger"):
        response = await database_exception_handler(mock_request, test_error)

    assert response.status_code == status.HTTP_404_NOT_FOUND

    import json

    body = json.loads(response.body)
    assert body["type"] == "NotFoundError"


@pytest.mark.asyncio
async def test_validation_error_returns_422():
    """Test that ValidationError returns 422 status code."""
    mock_request = MagicMock()
    mock_request.url.path = "/test/path"

    test_error = ValidationError("Validation failed")

    with patch("app.core.exceptions.logger"):
        response = await database_exception_handler(mock_request, test_error)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    import json

    body = json.loads(response.body)
    assert body["type"] == "ValidationError"


def test_setup_exception_handlers_registers_handlers():
    """Test that setup_exception_handlers registers global handlers."""
    mock_app = MagicMock()

    with patch("app.core.exceptions.logger"):
        setup_exception_handlers(mock_app)

    # Verify add_exception_handler was called
    mock_app.add_exception_handler.assert_called_once()

    # Verify it was called with DatabaseError and the handler
    args = mock_app.add_exception_handler.call_args[0]
    assert args[0] == DatabaseError
    assert args[1] == database_exception_handler
