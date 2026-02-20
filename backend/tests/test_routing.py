"""
Tests for the LangGraph routing logic.

All LLM calls are mocked — no real API calls are made in these tests.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock

from state import CouncilState, APPROVAL_THRESHOLD, MAX_ITERATIONS
from services.graph_builder import route_after_critic, create_initial_state


class TestRouteAfterCritic:
    """Unit tests for the conditional edge routing function."""

    def _make_state(self, route_decision: str, iteration_count: int = 1) -> CouncilState:
        state = create_initial_state("test topic", "test-run")
        state["route_decision"] = route_decision
        state["iteration_count"] = iteration_count
        return state

    def test_approve_routes_to_writer(self):
        state = self._make_state("approve")
        assert route_after_critic(state) == "writer_agent"

    def test_rework_routes_to_master(self):
        state = self._make_state("rework")
        assert route_after_critic(state) == "master_agent"

    def test_empty_decision_defaults_to_rework(self):
        state = self._make_state("")
        assert route_after_critic(state) == "master_agent"

    def test_unknown_decision_defaults_to_rework(self):
        state = self._make_state("unknown_value")
        assert route_after_critic(state) == "master_agent"


class TestCriticAgentParsing:
    """Unit tests for the critic agent's response parser."""

    def test_parse_valid_approve_response(self):
        from agents.critic_agent import _parse_critic_response

        content = "SCORE: 9\nVERDICT: approve\nFEEDBACK:\nExcellent work."
        score, verdict, feedback = _parse_critic_response(content)
        assert score == 9.0
        assert verdict == "approve"
        assert "Excellent" in feedback

    def test_parse_valid_rework_response(self):
        from agents.critic_agent import _parse_critic_response

        content = "SCORE: 5\nVERDICT: rework\nFEEDBACK:\nNeeds more detail."
        score, verdict, feedback = _parse_critic_response(content)
        assert score == 5.0
        assert verdict == "rework"
        assert "detail" in feedback

    def test_parse_score_clamped_to_0_10(self):
        from agents.critic_agent import _parse_critic_response

        content = "SCORE: 15\nVERDICT: approve\nFEEDBACK:\nToo high score."
        score, verdict, feedback = _parse_critic_response(content)
        assert score == 10.0

    def test_parse_missing_score_defaults_to_0(self):
        from agents.critic_agent import _parse_critic_response

        content = "No structured response at all."
        score, verdict, feedback = _parse_critic_response(content)
        assert score == 0.0
        assert verdict == "rework"

    def test_threshold_boundary_exactly_8_approves(self):
        from agents.critic_agent import _parse_critic_response

        content = f"SCORE: {APPROVAL_THRESHOLD}\nVERDICT: approve\nFEEDBACK:\nGood."
        score, verdict, _ = _parse_critic_response(content)
        assert score == APPROVAL_THRESHOLD
        assert verdict == "approve"


class TestMasterAgentPromptBuilding:
    """Unit tests for the master agent's prompt construction."""

    def test_first_iteration_prompt_has_no_feedback_block(self):
        from agents.master_agent import _build_master_prompt

        state = create_initial_state("Test topic", "run-1")
        prompt = _build_master_prompt(state)
        assert "Test topic" in prompt
        assert "feedback" not in prompt.lower() or "Feedback" not in prompt

    def test_rework_prompt_includes_feedback(self):
        from agents.master_agent import _build_master_prompt

        state = create_initial_state("Test topic", "run-1")
        state["current_draft"] = "My draft"
        state["feedback_history"] = ["Score: 5/10\nNeeds more structure."]
        prompt = _build_master_prompt(state)
        assert "My draft" in prompt
        assert "Needs more structure" in prompt

    def test_rework_prompt_includes_all_feedback_rounds(self):
        from agents.master_agent import _build_master_prompt

        state = create_initial_state("Topic", "run-2")
        state["current_draft"] = "Draft v2"
        state["feedback_history"] = ["First feedback", "Second feedback"]
        prompt = _build_master_prompt(state)
        assert "First feedback" in prompt
        assert "Second feedback" in prompt
        assert "2 round" in prompt


class TestCriticSafetyValve:
    """Tests for the MAX_ITERATIONS safety valve in the critic agent."""

    def test_safety_valve_forces_approve_at_max_iterations(self):
        from agents.critic_agent import critic_agent_node

        state = create_initial_state("topic", "run-safety")
        state["iteration_count"] = MAX_ITERATIONS
        state["current_draft"] = "Some draft"

        result = critic_agent_node(state)

        assert result["route_decision"] == "approve"
        assert result["critic_score"] == APPROVAL_THRESHOLD

    def test_safety_valve_not_triggered_below_max(self):
        """Below MAX_ITERATIONS the real LLM call would happen — mock it."""
        from agents.critic_agent import critic_agent_node

        mock_response = MagicMock()
        mock_response.content = "SCORE: 4\nVERDICT: rework\nFEEDBACK:\nNeeds work."

        with patch("agents.critic_agent.ChatAnthropic") as MockLLM:
            MockLLM.return_value.invoke.return_value = mock_response

            state = create_initial_state("topic", "run-below-max")
            state["iteration_count"] = MAX_ITERATIONS - 1
            state["current_draft"] = "Draft"

            result = critic_agent_node(state)

        assert result["route_decision"] == "rework"
        assert result["critic_score"] == 4.0


class TestMasterAgentNode:
    """Integration-style tests for master_agent_node with mocked LLM."""

    def test_master_agent_returns_draft(self):
        from agents.master_agent import master_agent_node

        mock_response = MagicMock()
        mock_response.content = "This is a generated draft about AI."

        with patch("agents.master_agent.ChatAnthropic") as MockLLM:
            MockLLM.return_value.invoke.return_value = mock_response

            state = create_initial_state("AI basics", "run-master-1")
            result = master_agent_node(state)

        assert result["current_draft"] == "This is a generated draft about AI."
        assert result["active_node"] == "master_agent"
        assert result["iteration_count"] == 1

    def test_master_agent_increments_iteration_count(self):
        from agents.master_agent import master_agent_node

        mock_response = MagicMock()
        mock_response.content = "Draft"

        with patch("agents.master_agent.ChatAnthropic") as MockLLM:
            MockLLM.return_value.invoke.return_value = mock_response

            state = create_initial_state("topic", "run-master-2")
            state["iteration_count"] = 3
            result = master_agent_node(state)

        assert result["iteration_count"] == 4


class TestWriterAgentNode:
    """Tests for writer_agent_node with mocked LLM."""

    def test_writer_returns_polished_draft(self):
        from agents.writer_agent import writer_agent_node

        mock_response = MagicMock()
        mock_response.content = "Polished and professional document."

        with patch("agents.writer_agent.ChatAnthropic") as MockLLM:
            MockLLM.return_value.invoke.return_value = mock_response

            state = create_initial_state("Machine Learning", "run-writer-1")
            state["current_draft"] = "Raw draft content"
            result = writer_agent_node(state)

        assert result["current_draft"] == "Polished and professional document."
        assert result["active_node"] == "writer_agent"
        assert result["route_decision"] == "done"
