"""Unit tests for health check endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.health import database_health_check, health_check, readiness_check


@pytest.mark.asyncio
async def test_health_check_returns_healthy():
    """Test that basic health check returns healthy status."""
    response = await health_check()

    assert response["status"] == "healthy"
    assert response["service"] == "api"


@pytest.mark.asyncio
async def test_database_health_check_success():
    """Test database health check with successful connection."""
    # Create mock session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=MagicMock())

    # Call health check
    response = await database_health_check(db=mock_session)

    # Verify response
    assert response["status"] == "healthy"
    assert response["service"] == "database"
    assert response["provider"] == "postgresql"

    # Verify execute was called with SELECT 1
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_database_health_check_failure():
    """Test database health check when connection fails."""
    # Create mock session that raises an exception
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(side_effect=Exception("Connection failed"))

    # Call health check and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await database_health_check(db=mock_session)

    # Verify exception details
    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Database connection failed" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_readiness_check_success():
    """Test readiness check when all dependencies are healthy."""
    # Create mock session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=MagicMock())

    # Call readiness check
    response = await readiness_check(db=mock_session)

    # Verify response
    assert response["status"] == "ready"
    assert response["environment"] in ["development", "production", "staging"]
    assert response["database"] == "connected"


@pytest.mark.asyncio
async def test_readiness_check_failure():
    """Test readiness check when database is not ready."""
    # Create mock session that raises an exception
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(side_effect=Exception("Database not ready"))

    # Call readiness check and expect HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await readiness_check(db=mock_session)

    # Verify exception details
    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Application not ready" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_database_health_check_logs_on_success():
    """Test that database health check logs on success."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(return_value=MagicMock())

    with patch("app.core.health.logger") as mock_logger:
        await database_health_check(db=mock_session)

        # Verify debug log was called
        mock_logger.debug.assert_called_once_with("database.health_check.success")


@pytest.mark.asyncio
async def test_database_health_check_logs_on_failure():
    """Test that database health check logs errors with exc_info."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute = AsyncMock(side_effect=Exception("Test error"))

    with patch("app.core.health.logger") as mock_logger:
        try:
            await database_health_check(db=mock_session)
        except HTTPException:
            pass

        # Verify error log was called with exc_info=True
        mock_logger.error.assert_called_once()
        call_kwargs = mock_logger.error.call_args[1]
        assert call_kwargs["exc_info"] is True
