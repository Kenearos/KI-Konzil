"""
Integration tests for the FastAPI REST endpoints.

Uses httpx.AsyncClient with the TestClient pattern — no real LLM calls.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from main import app
from api.run_store import run_store


@pytest.fixture(autouse=True)
def clean_run_store():
    """Reset the run store before each test."""
    run_store._store.clear()
    yield
    run_store._store.clear()


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check_returns_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestStartCouncilRun:
    def test_start_run_returns_202_with_run_id(self):
        with patch("api.routes._execute_run", new_callable=AsyncMock):
            response = client.post(
                "/api/councils/run",
                json={"input_topic": "Erkläre maschinelles Lernen"},
            )
        assert response.status_code == 202
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"
        assert len(data["run_id"]) == 36  # UUID format

    def test_start_run_rejects_empty_topic(self):
        response = client.post("/api/councils/run", json={"input_topic": ""})
        assert response.status_code == 422  # Pydantic validation error

    def test_start_run_rejects_missing_topic(self):
        response = client.post("/api/councils/run", json={})
        assert response.status_code == 422


class TestGetCouncilResult:
    def test_get_pending_run(self):
        run_store.create("test-run-id", "Test topic")
        response = client.get("/api/councils/run/test-run-id")
        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == "test-run-id"
        assert data["status"] == "pending"

    def test_get_completed_run(self):
        run_store.create("completed-run", "Topic")
        run_store.update("completed-run", {
            "status": "completed",
            "final_draft": "Final polished document.",
            "critic_score": 9.0,
            "iteration_count": 2,
        })
        response = client.get("/api/councils/run/completed-run")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["final_draft"] == "Final polished document."
        assert data["critic_score"] == 9.0
        assert data["iteration_count"] == 2

    def test_get_nonexistent_run_returns_404(self):
        response = client.get("/api/councils/run/does-not-exist")
        assert response.status_code == 404

    def test_get_failed_run(self):
        run_store.create("failed-run", "Topic")
        run_store.update("failed-run", {
            "status": "failed",
            "error": "API connection timeout",
        })
        response = client.get("/api/councils/run/failed-run")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "timeout" in data["error"]
