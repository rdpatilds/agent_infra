"""Integration tests for database connectivity.

CRITICAL: These tests MUST use fixtures (test_db_session, test_db_engine)
instead of importing from app.core.database directly.

These tests require a running PostgreSQL database.
Start with: docker-compose up -d db

Run with: pytest -v -m integration
Skip with: pytest -v -m "not integration"
"""

import pytest
from sqlalchemy import text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_connection(test_db_session):
    """Test basic database connectivity with real PostgreSQL.

    IMPORTANT: Uses test_db_session fixture, NOT module imports.
    This ensures the engine is bound to the correct event loop.

    Args:
        test_db_session: Database session from fixture.
    """
    result = await test_db_session.execute(text("SELECT 1 as value"))
    value = result.scalar_one()
    assert value == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_session_lifecycle(test_db_session):
    """Test that database sessions work correctly through their lifecycle.

    Args:
        test_db_session: Database session from fixture.
    """
    # Execute a simple query
    result = await test_db_session.execute(text("SELECT current_database()"))
    db_name = result.scalar_one()

    # Verify we got a database name
    assert db_name is not None
    assert isinstance(db_name, str)
    assert len(db_name) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_metadata_operations(test_db_engine):
    """Test database metadata operations.

    Args:
        test_db_engine: Database engine from fixture.
    """
    from app.core.database import Base

    # Verify Base metadata is accessible
    assert Base.metadata is not None

    # Test that we can introspect the database
    async with test_db_engine.connect() as conn:
        # Check PostgreSQL version
        result = await conn.execute(text("SELECT version()"))
        version = result.scalar_one()
        assert "PostgreSQL" in version


@pytest.mark.integration
@pytest.mark.asyncio
async def test_transaction_rollback(test_db_session):
    """Test that transaction rollback works correctly.

    Args:
        test_db_session: Database session from fixture.
    """
    # Create a temporary table for testing
    await test_db_session.execute(
        text("CREATE TEMP TABLE test_rollback (id INTEGER, value TEXT)")
    )

    # Insert a value
    await test_db_session.execute(
        text("INSERT INTO test_rollback (id, value) VALUES (1, 'test')")
    )

    # Rollback the transaction
    await test_db_session.rollback()

    # Verify table still exists but data was rolled back
    # Note: TEMP table creation is not rolled back, but data is
    result = await test_db_session.execute(text("SELECT COUNT(*) FROM test_rollback"))
    count = result.scalar_one()
    assert count == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_connection_pool_management(test_db_engine):
    """Test that connection pool handles multiple connections correctly.

    Args:
        test_db_engine: Database engine from fixture.
    """
    # Open multiple connections simultaneously
    connections = []
    try:
        for _ in range(3):
            conn = await test_db_engine.connect()
            connections.append(conn)

            # Execute a query on each connection
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar_one()
            assert value == 1

    finally:
        # Close all connections
        for conn in connections:
            await conn.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_connection_recovery_after_error(test_db_session):
    """Test that connections can recover after errors.

    Args:
        test_db_session: Database session from fixture.
    """
    # Execute an invalid query to cause an error
    try:
        await test_db_session.execute(text("SELECT * FROM nonexistent_table"))
    except Exception:
        # Expected to fail
        pass

    # Rollback to clear the error state
    await test_db_session.rollback()

    # Verify we can still use the session
    result = await test_db_session.execute(text("SELECT 1"))
    value = result.scalar_one()
    assert value == 1
