"""
Tests for health check endpoints.
"""

import pytest
from httpx import AsyncClient
from backend.app.api import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "healthy"


@pytest.mark.asyncio
async def test_database_health():
    """Test database health check."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health/database")

    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "database"