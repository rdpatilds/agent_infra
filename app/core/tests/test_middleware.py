"""Tests for middleware module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from starlette.responses import Response

from app.core.logging import get_request_id
from app.core.middleware import RequestLoggingMiddleware


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    return FastAPI()


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    with patch("app.core.middleware.logger") as logger:
        yield logger


@pytest.mark.asyncio
async def test_middleware_generates_request_id(app, mock_logger):
    """Test RequestLoggingMiddleware generates request_id when not provided."""
    middleware = RequestLoggingMiddleware(app)

    # Create mock request without X-Request-ID header
    request = MagicMock(spec=Request)
    request.headers = {}
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"

    # Create mock response
    response = Response()
    call_next = AsyncMock(return_value=response)

    # Process request
    result = await middleware.dispatch(request, call_next)

    # Verify request_id was generated and added to response
    assert "X-Request-ID" in result.headers
    assert len(result.headers["X-Request-ID"]) > 0

    # Verify logging calls
    assert mock_logger.info.call_count >= 2  # started and completed


@pytest.mark.asyncio
async def test_middleware_uses_provided_request_id(app, mock_logger):
    """Test middleware uses X-Request-ID header if provided."""
    middleware = RequestLoggingMiddleware(app)

    test_request_id = "test-request-123"

    # Create mock request with X-Request-ID header
    request = MagicMock(spec=Request)
    request.headers = {"X-Request-ID": test_request_id}
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"

    response = Response()
    call_next = AsyncMock(return_value=response)

    # Process request
    result = await middleware.dispatch(request, call_next)

    # Verify the same request_id is in response
    assert result.headers["X-Request-ID"] == test_request_id

    # Verify request_id is in context
    assert get_request_id() == test_request_id


@pytest.mark.asyncio
async def test_middleware_logs_request_started_and_completed(app, mock_logger):
    """Test middleware logs request.started and request.completed."""
    middleware = RequestLoggingMiddleware(app)

    request = MagicMock(spec=Request)
    request.headers = {}
    request.method = "POST"
    request.url.path = "/api/users"
    request.client.host = "192.168.1.1"

    response = Response(status_code=201)
    call_next = AsyncMock(return_value=response)

    await middleware.dispatch(request, call_next)

    # Verify request.started was logged
    assert mock_logger.info.call_count >= 2
    started_call = mock_logger.info.call_args_list[0]
    assert started_call[0][0] == "request.started"
    assert started_call[1]["method"] == "POST"
    assert started_call[1]["path"] == "/api/users"
    assert started_call[1]["client_host"] == "192.168.1.1"

    # Verify request.completed was logged
    completed_call = mock_logger.info.call_args_list[1]
    assert completed_call[0][0] == "request.completed"
    assert completed_call[1]["method"] == "POST"
    assert completed_call[1]["path"] == "/api/users"
    assert completed_call[1]["status_code"] == 201
    assert "duration_seconds" in completed_call[1]


@pytest.mark.asyncio
async def test_middleware_logs_request_failed_on_exception(app, mock_logger):
    """Test middleware logs request.failed with exc_info on exceptions."""
    middleware = RequestLoggingMiddleware(app)

    request = MagicMock(spec=Request)
    request.headers = {}
    request.method = "GET"
    request.url.path = "/api/error"
    request.client.host = "127.0.0.1"

    # Simulate an exception during request processing
    test_exception = ValueError("Test error")
    call_next = AsyncMock(side_effect=test_exception)

    with pytest.raises(ValueError):
        await middleware.dispatch(request, call_next)

    # Verify request.failed was logged
    assert mock_logger.error.called
    error_call = mock_logger.error.call_args
    assert error_call[0][0] == "request.failed"
    assert error_call[1]["method"] == "GET"
    assert error_call[1]["path"] == "/api/error"
    assert error_call[1]["error"] == "Test error"
    assert error_call[1]["exc_info"] is True
    assert "duration_seconds" in error_call[1]


@pytest.mark.asyncio
async def test_request_id_in_response_headers(app, mock_logger):
    """Test X-Request-ID appears in response headers."""
    middleware = RequestLoggingMiddleware(app)

    request = MagicMock(spec=Request)
    request.headers = {}
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"

    response = Response()
    call_next = AsyncMock(return_value=response)

    result = await middleware.dispatch(request, call_next)

    # Verify X-Request-ID is present in response headers
    assert "X-Request-ID" in result.headers
    request_id = result.headers["X-Request-ID"]
    assert isinstance(request_id, str)
    assert len(request_id) > 0
