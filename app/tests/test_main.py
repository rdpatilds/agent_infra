"""Tests for main FastAPI application."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns correct JSON structure."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Obsidian Agent Project"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_docs_endpoint_accessible():
    """Test /docs endpoint is accessible."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/docs")

    # Should return 200 for OpenAPI docs
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json_accessible():
    """Test /openapi.json endpoint is accessible."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "Obsidian Agent Project"
    assert data["info"]["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_app_metadata():
    """Test application has correct metadata from settings."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Get OpenAPI schema which includes app metadata
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Verify application metadata matches settings
    assert schema["info"]["title"] == "Obsidian Agent Project"
    assert schema["info"]["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_cors_headers_present():
    """Test CORS headers are present in responses."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/", headers={"Origin": "http://localhost:3000"})

    # Check for CORS headers
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_request_id_in_response():
    """Test X-Request-ID is added to response headers."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    # Verify X-Request-ID is in response headers
    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) > 0


@pytest.mark.asyncio
async def test_custom_request_id_preserved():
    """Test custom X-Request-ID from request is preserved in response."""
    custom_request_id = "test-request-123"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/", headers={"X-Request-ID": custom_request_id})

    # Verify the custom request ID is in response
    assert response.headers["x-request-id"] == custom_request_id
