"""
Tests for the FastAPI endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    """Ensure DB tables exist before each test."""
    await init_db()


@pytest.mark.anyio
async def test_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_traffic_history():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/traffic/history")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "count" in data


@pytest.mark.anyio
async def test_pollution_history():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/pollution/history")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data


@pytest.mark.anyio
async def test_snapshot():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/snapshot")
    assert resp.status_code == 200
