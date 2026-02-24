"""
Tests for the run history service and CouncilRun model.

DB-backed tests use an in-memory SQLite database for full isolation —
the same approach as test_blueprint_service.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.blueprint import Base  # CouncilRun shares this Base
from services.run_service import create_run, get_run, list_runs, update_run


# ---------------------------------------------------------------------------
# In-memory SQLite test database
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def session():
    """Create all tables and yield a fresh session. Tables are dropped after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as sess:
        yield sess

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# CouncilRun model serialization (no DB required)
# ---------------------------------------------------------------------------

class TestCouncilRunModel:
    """Tests for the CouncilRun SQLAlchemy model."""

    def test_to_dict_serialization(self):
        from models.council_run import CouncilRun
        from datetime import datetime, timezone

        run = CouncilRun(
            id="test-id",
            blueprint_id="bp-id",
            input_topic="Test topic",
            status="completed",
            execution_mode="auto-pilot",
            final_draft="Final text",
            critic_score=8.5,
            iteration_count=3,
            active_node="done",
            error=None,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            completed_at=datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc),
        )

        d = run.to_dict()
        assert d["id"] == "test-id"
        assert d["blueprint_id"] == "bp-id"
        assert d["status"] == "completed"
        assert d["critic_score"] == 8.5
        assert d["iteration_count"] == 3
        assert d["created_at"] is not None
        assert d["completed_at"] is not None

    def test_to_dict_with_none_timestamps(self):
        from models.council_run import CouncilRun

        run = CouncilRun(
            id="test-id",
            input_topic="Test",
            status="pending",
            execution_mode="god-mode",
            created_at=None,
            completed_at=None,
        )

        d = run.to_dict()
        assert d["created_at"] is None
        assert d["completed_at"] is None
        assert d["execution_mode"] == "god-mode"


# ---------------------------------------------------------------------------
# create_run
# ---------------------------------------------------------------------------

class TestCreateRun:
    """Tests for the create_run service function."""

    @pytest.mark.asyncio
    async def test_create_run_stores_correct_fields(self, session):
        run = await create_run(session, run_id="run-001", input_topic="Test topic")

        assert run.id == "run-001"
        assert run.input_topic == "Test topic"
        assert run.status == "pending"
        assert run.execution_mode == "auto-pilot"
        assert run.blueprint_id is None
        assert run.completed_at is None

    @pytest.mark.asyncio
    async def test_create_run_with_blueprint_id(self, session):
        run = await create_run(
            session,
            run_id="run-002",
            input_topic="Topic",
            blueprint_id="bp-abc",
        )

        assert run.blueprint_id == "bp-abc"

    @pytest.mark.asyncio
    async def test_create_run_with_god_mode(self, session):
        run = await create_run(
            session,
            run_id="run-003",
            input_topic="Topic",
            execution_mode="god-mode",
        )

        assert run.execution_mode == "god-mode"

    @pytest.mark.asyncio
    async def test_create_run_sets_created_at(self, session):
        run = await create_run(session, run_id="run-004", input_topic="Topic")

        assert run.created_at is not None


# ---------------------------------------------------------------------------
# get_run
# ---------------------------------------------------------------------------

class TestGetRun:
    """Tests for the get_run service function."""

    @pytest.mark.asyncio
    async def test_get_run_returns_existing_run(self, session):
        await create_run(session, run_id="run-100", input_topic="Get test")
        fetched = await get_run(session, "run-100")

        assert fetched is not None
        assert fetched.id == "run-100"
        assert fetched.input_topic == "Get test"

    @pytest.mark.asyncio
    async def test_get_run_returns_none_for_unknown_id(self, session):
        result = await get_run(session, "nonexistent-id")

        assert result is None


# ---------------------------------------------------------------------------
# list_runs
# ---------------------------------------------------------------------------

class TestListRuns:
    """Tests for the list_runs service function."""

    @pytest.mark.asyncio
    async def test_list_runs_empty(self, session):
        runs = await list_runs(session)

        assert runs == []

    @pytest.mark.asyncio
    async def test_list_runs_returns_all(self, session):
        await create_run(session, run_id="run-a", input_topic="Topic A")
        await create_run(session, run_id="run-b", input_topic="Topic B")
        runs = await list_runs(session)

        assert len(runs) == 2

    @pytest.mark.asyncio
    async def test_list_runs_limit(self, session):
        for i in range(5):
            await create_run(session, run_id=f"run-{i}", input_topic=f"Topic {i}")

        runs = await list_runs(session, limit=3)

        assert len(runs) == 3

    @pytest.mark.asyncio
    async def test_list_runs_offset(self, session):
        for i in range(4):
            await create_run(session, run_id=f"run-{i}", input_topic=f"Topic {i}")

        runs_all = await list_runs(session)
        runs_offset = await list_runs(session, offset=2)

        # The offset skips the first 2 runs (most recent first)
        assert len(runs_offset) == 2
        assert runs_offset[0].id == runs_all[2].id


# ---------------------------------------------------------------------------
# update_run
# ---------------------------------------------------------------------------

class TestUpdateRun:
    """Tests for the update_run service function."""

    @pytest.mark.asyncio
    async def test_update_run_returns_none_for_unknown_id(self, session):
        result = await update_run(session, "ghost-id", {"status": "running"})

        assert result is None

    @pytest.mark.asyncio
    async def test_update_run_changes_status(self, session):
        await create_run(session, run_id="run-u1", input_topic="Topic")
        updated = await update_run(session, "run-u1", {"status": "running"})

        assert updated is not None
        assert updated.status == "running"

    @pytest.mark.asyncio
    async def test_update_run_sets_completed_at_when_completed(self, session):
        await create_run(session, run_id="run-u2", input_topic="Topic")
        updated = await update_run(session, "run-u2", {"status": "completed"})

        assert updated is not None
        assert updated.status == "completed"
        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_run_sets_completed_at_when_failed(self, session):
        await create_run(session, run_id="run-u3", input_topic="Topic")
        updated = await update_run(session, "run-u3", {"status": "failed", "error": "Timeout"})

        assert updated is not None
        assert updated.status == "failed"
        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_run_does_not_set_completed_at_for_running(self, session):
        await create_run(session, run_id="run-u4", input_topic="Topic")
        updated = await update_run(session, "run-u4", {"status": "running"})

        assert updated is not None
        assert updated.completed_at is None

    @pytest.mark.asyncio
    async def test_update_run_stores_final_draft_and_score(self, session):
        await create_run(session, run_id="run-u5", input_topic="Topic")
        updated = await update_run(
            session,
            "run-u5",
            {
                "status": "completed",
                "final_draft": "Polished text",
                "critic_score": 9.0,
                "iteration_count": 2,
            },
        )

        assert updated.final_draft == "Polished text"
        assert updated.critic_score == 9.0
        assert updated.iteration_count == 2

    @pytest.mark.asyncio
    async def test_update_run_ignores_unknown_fields(self, session):
        """Unknown keys in the updates dict are silently skipped via hasattr check."""
        await create_run(session, run_id="run-u6", input_topic="Topic")
        # "nonexistent_field" does not exist on CouncilRun — should not raise
        updated = await update_run(
            session, "run-u6", {"status": "running", "nonexistent_field": "value"}
        )

        assert updated is not None
        assert updated.status == "running"


# ---------------------------------------------------------------------------
# Run history routes (lightweight — service is mocked)
# ---------------------------------------------------------------------------

class TestRunHistoryRoutes:
    """Tests for the run history API routes."""

    @pytest.mark.asyncio
    async def test_list_runs_empty(self):
        """List runs returns empty list when no runs exist."""
        from api.run_history_routes import list_all_runs

        mock_session = AsyncMock()

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        with patch("services.run_service.list_runs") as mock_list:
            mock_list.return_value = []
            result = await list_all_runs(limit=50, offset=0, session=mock_session)
            assert result == []
