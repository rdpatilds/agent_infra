"""Pytest fixtures for integration tests.

IMPORTANT: Integration tests MUST use these fixtures instead of
importing AsyncSessionLocal/engine from app.core.database directly.

Why? The module-level engine in database.py is bound to the first
event loop. pytest-asyncio creates new loops per test. Using fixtures
ensures each test gets an engine bound to its own loop, avoiding
"Future attached to different loop" errors.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create fresh database engine for each test.

    This ensures each test has an engine bound to its own event loop,
    preventing "Future attached to different loop" errors.

    Yields:
        AsyncEngine: Fresh async database engine.
    """
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=False,  # Quiet in tests
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine):
    """Create fresh database session for each test.

    Uses the test_db_engine fixture to ensure proper event loop binding.

    Args:
        test_db_engine: Database engine from test_db_engine fixture.

    Yields:
        AsyncSession: Fresh async database session.
    """
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with async_session() as session:
        yield session
