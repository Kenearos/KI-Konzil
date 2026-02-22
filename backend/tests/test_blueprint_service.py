"""
Tests for the blueprint CRUD service and API endpoints.

Uses an in-memory SQLite database for isolation.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.blueprint import Base
from services.blueprint_service import (
    create_blueprint,
    delete_blueprint,
    get_blueprint,
    list_blueprints,
    update_blueprint,
)


# ---------------------------------------------------------------------------
# Test database setup (in-memory SQLite)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session():
    """Create tables and yield a fresh session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as sess:
        yield sess

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_NODES = [
    {
        "id": "node-1",
        "label": "Master",
        "systemPrompt": "You are the master.",
        "model": "claude-3-5-sonnet",
        "tools": {"webSearch": False, "pdfReader": False},
        "position": {"x": 0, "y": 0},
    },
    {
        "id": "node-2",
        "label": "Critic",
        "systemPrompt": "You evaluate drafts.",
        "model": "gpt-4o",
        "tools": {"webSearch": True, "pdfReader": False},
        "position": {"x": 300, "y": 0},
    },
]

SAMPLE_EDGES = [
    {"id": "edge-1", "source": "node-1", "target": "node-2", "type": "linear"},
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBlueprintCRUD:
    @pytest.mark.asyncio
    async def test_create_blueprint(self, session):
        bp = await create_blueprint(session, "Test Council", SAMPLE_NODES, SAMPLE_EDGES)
        assert bp.id is not None
        assert bp.name == "Test Council"
        assert bp.version == 1
        assert len(bp.nodes) == 2
        assert len(bp.edges) == 1

    @pytest.mark.asyncio
    async def test_create_with_custom_id(self, session):
        bp = await create_blueprint(
            session, "Custom ID", SAMPLE_NODES, SAMPLE_EDGES, blueprint_id="my-custom-id"
        )
        assert bp.id == "my-custom-id"

    @pytest.mark.asyncio
    async def test_get_blueprint(self, session):
        bp = await create_blueprint(session, "Get Test", SAMPLE_NODES, SAMPLE_EDGES)
        fetched = await get_blueprint(session, bp.id)
        assert fetched is not None
        assert fetched.name == "Get Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, session):
        result = await get_blueprint(session, "nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_blueprints(self, session):
        await create_blueprint(session, "First", SAMPLE_NODES, SAMPLE_EDGES)
        await create_blueprint(session, "Second", SAMPLE_NODES, SAMPLE_EDGES)
        all_bps = await list_blueprints(session)
        assert len(all_bps) == 2

    @pytest.mark.asyncio
    async def test_update_blueprint_name(self, session):
        bp = await create_blueprint(session, "Original", SAMPLE_NODES, SAMPLE_EDGES)
        updated = await update_blueprint(session, bp.id, name="Renamed")
        assert updated is not None
        assert updated.name == "Renamed"

    @pytest.mark.asyncio
    async def test_update_blueprint_nodes(self, session):
        bp = await create_blueprint(session, "Nodes Test", SAMPLE_NODES, SAMPLE_EDGES)
        new_nodes = [SAMPLE_NODES[0]]  # Remove second node
        updated = await update_blueprint(session, bp.id, nodes=new_nodes)
        assert updated is not None
        assert len(updated.nodes) == 1

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_none(self, session):
        result = await update_blueprint(session, "ghost-id", name="New Name")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_blueprint(self, session):
        bp = await create_blueprint(session, "To Delete", SAMPLE_NODES, SAMPLE_EDGES)
        deleted = await delete_blueprint(session, bp.id)
        assert deleted is True
        assert await get_blueprint(session, bp.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_returns_false(self, session):
        deleted = await delete_blueprint(session, "ghost-id")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_to_dict_format(self, session):
        bp = await create_blueprint(session, "Dict Test", SAMPLE_NODES, SAMPLE_EDGES)
        d = bp.to_dict()
        assert d["id"] == bp.id
        assert d["version"] == 1
        assert d["name"] == "Dict Test"
        assert "createdAt" in d
        assert "updatedAt" in d
        assert isinstance(d["nodes"], list)
        assert isinstance(d["edges"], list)
