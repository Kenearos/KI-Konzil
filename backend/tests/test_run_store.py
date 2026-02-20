"""Tests for the in-memory RunStore."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.run_store import RunStore


class TestRunStore:
    def setup_method(self):
        self.store = RunStore()

    def test_create_and_get(self):
        self.store.create("run-1", "Test topic")
        run = self.store.get("run-1")
        assert run is not None
        assert run["run_id"] == "run-1"
        assert run["input_topic"] == "Test topic"
        assert run["status"] == "pending"

    def test_get_nonexistent_returns_none(self):
        assert self.store.get("nonexistent") is None

    def test_update_status(self):
        self.store.create("run-2", "Topic")
        self.store.update("run-2", {"status": "running"})
        assert self.store.get("run-2")["status"] == "running"

    def test_update_nonexistent_is_noop(self):
        """Updating a non-existent run should not raise."""
        self.store.update("ghost-run", {"status": "running"})

    def test_delete(self):
        self.store.create("run-3", "Topic")
        self.store.delete("run-3")
        assert self.store.get("run-3") is None

    def test_delete_nonexistent_is_noop(self):
        self.store.delete("ghost-run")

    def test_update_partial_fields(self):
        self.store.create("run-4", "Topic")
        self.store.update("run-4", {"status": "completed", "final_draft": "Result text"})
        run = self.store.get("run-4")
        assert run["status"] == "completed"
        assert run["final_draft"] == "Result text"
        assert run["input_topic"] == "Topic"  # original field preserved

    def test_multiple_runs_independent(self):
        self.store.create("run-a", "Topic A")
        self.store.create("run-b", "Topic B")
        self.store.update("run-a", {"status": "running"})
        assert self.store.get("run-b")["status"] == "pending"
