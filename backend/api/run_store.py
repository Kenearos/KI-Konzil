"""
In-memory run store for Phase 1.

Tracks the status and results of council runs by run_id. This is intentionally
simple for Phase 1. Phase 3+ will replace this with a PostgreSQL-backed store.
"""

from typing import Any, Dict, Optional
import threading


class RunStore:
    """Thread-safe in-memory store for council run state."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, run_id: str, input_topic: str) -> None:
        with self._lock:
            self._store[run_id] = {
                "run_id": run_id,
                "input_topic": input_topic,
                "status": "pending",
                "final_draft": None,
                "critic_score": None,
                "iteration_count": None,
                "active_node": None,
                "error": None,
            }

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._store.get(run_id)

    def update(self, run_id: str, updates: Dict[str, Any]) -> None:
        with self._lock:
            if run_id in self._store:
                self._store[run_id].update(updates)

    def delete(self, run_id: str) -> None:
        with self._lock:
            self._store.pop(run_id, None)


# Singleton instance shared across the application
run_store = RunStore()
