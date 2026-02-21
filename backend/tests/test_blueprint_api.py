"""
Integration tests for the blueprint CRUD REST endpoints.

Overrides the database dependency to use an in-memory SQLite database.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.blueprint import Base
from database import get_session
from main import app


# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create and tear down tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Sample payload
# ---------------------------------------------------------------------------

SAMPLE_BLUEPRINT = {
    "version": 1,
    "name": "Test Council",
    "nodes": [
        {
            "id": "node-1",
            "label": "Master",
            "systemPrompt": "You are the master writer.",
            "model": "claude-3-5-sonnet",
            "tools": {"webSearch": False, "pdfReader": False},
            "position": {"x": 0, "y": 0},
        },
        {
            "id": "node-2",
            "label": "Critic",
            "systemPrompt": "You evaluate drafts.",
            "model": "claude-3-5-sonnet",
            "tools": {"webSearch": False, "pdfReader": False},
            "position": {"x": 300, "y": 0},
        },
    ],
    "edges": [
        {"id": "edge-1", "source": "node-1", "target": "node-2", "type": "linear"},
    ],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBlueprintEndpoints:
    @pytest.mark.asyncio
    async def test_create_blueprint(self, client):
        response = await client.post("/api/councils/", json=SAMPLE_BLUEPRINT)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Council"
        assert data["version"] == 1
        assert len(data["nodes"]) == 2
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_blueprints(self, client):
        await client.post("/api/councils/", json=SAMPLE_BLUEPRINT)
        await client.post(
            "/api/councils/",
            json={**SAMPLE_BLUEPRINT, "name": "Second Council"},
        )

        response = await client.get("/api/councils/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_blueprint(self, client):
        create_resp = await client.post("/api/councils/", json=SAMPLE_BLUEPRINT)
        bp_id = create_resp.json()["id"]

        response = await client.get(f"/api/councils/{bp_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Council"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_404(self, client):
        response = await client.get("/api/councils/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_blueprint(self, client):
        create_resp = await client.post("/api/councils/", json=SAMPLE_BLUEPRINT)
        bp_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/api/councils/{bp_id}",
            json={"name": "Renamed Council"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Renamed Council"

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_404(self, client):
        response = await client.put(
            "/api/councils/ghost-id",
            json={"name": "Ghost"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_blueprint(self, client):
        create_resp = await client.post("/api/councils/", json=SAMPLE_BLUEPRINT)
        bp_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/api/councils/{bp_id}")
        assert delete_resp.status_code == 204

        get_resp = await client.get(f"/api/councils/{bp_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_404(self, client):
        response = await client.delete("/api/councils/ghost-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_rejects_missing_name(self, client):
        payload = {**SAMPLE_BLUEPRINT}
        del payload["name"]
        response = await client.post("/api/councils/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_rejects_empty_name(self, client):
        payload = {**SAMPLE_BLUEPRINT, "name": ""}
        response = await client.post("/api/councils/", json=payload)
        assert response.status_code == 422
