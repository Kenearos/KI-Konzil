"""Tests for CouncilState structure and graph_builder helpers."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from state import CouncilState, APPROVAL_THRESHOLD, MAX_ITERATIONS
from services.graph_builder import create_initial_state


class TestCouncilState:
    def test_initial_state_fields(self):
        state = create_initial_state("Test topic", "run-001")
        assert state["input_topic"] == "Test topic"
        assert state["current_draft"] == ""
        assert state["feedback_history"] == []
        assert state["route_decision"] == ""
        assert state["messages"] == []
        assert state["iteration_count"] == 0
        assert state["critic_score"] is None
        assert state["run_id"] == "run-001"
        assert state["active_node"] == ""

    def test_approval_threshold_value(self):
        assert APPROVAL_THRESHOLD == 8.0

    def test_max_iterations_value(self):
        assert MAX_ITERATIONS == 5

    def test_state_is_typed_dict(self):
        """CouncilState should be instantiable as a plain dict."""
        state: CouncilState = {
            "input_topic": "AI",
            "current_draft": "draft",
            "feedback_history": ["fb1"],
            "route_decision": "rework",
            "messages": [],
            "iteration_count": 1,
            "critic_score": 6.0,
            "run_id": "x",
            "active_node": "critic_agent",
        }
        assert state["critic_score"] == 6.0
