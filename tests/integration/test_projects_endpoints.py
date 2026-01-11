import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_projects_requires_auth(client: AsyncClient):
    """Test that listing projects requires authentication"""
    response = await client.get("/api/v1/projects")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_projects_empty(client: AsyncClient, api_headers: dict):
    """Test listing projects when none exist"""
    response = await client.get("/api/v1/projects", headers=api_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_get_nonexistent_project(client: AsyncClient, api_headers: dict):
    """Test getting a project that doesn't exist"""
    response = await client.get("/api/v1/projects/999", headers=api_headers)

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
