"""
Tests for the run history service and CouncilRun model.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


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
