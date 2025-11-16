"""Unit tests for database configuration and session management."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, get_db


def test_base_class_configuration():
    """Test that Base class is properly configured for SQLAlchemy models."""
    # Verify Base is a DeclarativeBase
    assert hasattr(Base, "metadata")
    assert hasattr(Base, "registry")

    # Verify metadata is properly initialized
    assert Base.metadata is not None
    assert isinstance(Base.metadata.tables, dict)


@pytest.mark.asyncio
async def test_get_db_session_lifecycle():
    """Test that get_db creates and properly closes database sessions."""
    # Mock the async session maker
    mock_session = AsyncMock(spec=AsyncSession)

    with patch("app.core.database.AsyncSessionLocal") as mock_session_maker:
        # Configure the mock to return our mock session
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        # Use the generator
        async for session in get_db():
            # Verify we got a session
            assert session is mock_session
            # Verify session.close was NOT called yet (still in use)
            mock_session.close.assert_not_called()

        # After generator completes, verify close was called
        mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_closes_on_exception():
    """Test that get_db closes session even if exception occurs."""
    mock_session = AsyncMock(spec=AsyncSession)

    with patch("app.core.database.AsyncSessionLocal") as mock_session_maker:
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_session_maker.return_value.__aexit__.return_value = None

        try:
            async for session in get_db():
                # Simulate an error during session use
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify session was still closed despite the error
        mock_session.close.assert_called_once()


def test_engine_configuration():
    """Test that async engine is properly configured."""
    from app.core.database import engine

    # Verify engine exists and is properly configured
    assert engine is not None
    assert hasattr(engine, "dispose")

    # Verify engine URL is async (postgresql+asyncpg)
    assert "asyncpg" in str(engine.url)
