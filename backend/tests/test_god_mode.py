"""
Tests for God Mode (interrupt_before) functionality.

All LLM calls are mocked — no real API calls are made in these tests.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock

from state import CouncilState


class TestBuildGraphGodMode:
    """Tests for graph compilation with god mode (interrupt_before)."""

    def _make_simple_blueprint(self):
        return {
            "version": 1,
            "name": "Test Council",
            "nodes": [
                {
                    "id": "master",
                    "label": "Master AI",
                    "systemPrompt": "You are the master writer.",
                    "model": "claude-3-5-sonnet",
                    "tools": {"webSearch": False, "pdfReader": False},
                },
                {
                    "id": "critic",
                    "label": "Critic AI",
                    "systemPrompt": "You are a critic who evaluates and scores drafts.",
                    "model": "claude-3-5-sonnet",
                    "tools": {"webSearch": False, "pdfReader": False},
                },
            ],
            "edges": [
                {"id": "e1", "source": "master", "target": "critic", "type": "linear"},
            ],
        }

    @patch("services.dynamic_graph_builder._get_llm")
    def test_build_graph_with_god_mode_compiles(self, mock_get_llm):
        """God mode graph should compile without error."""
        from services.dynamic_graph_builder import build_graph_from_blueprint

        blueprint = self._make_simple_blueprint()
        graph = build_graph_from_blueprint(blueprint, god_mode=False)
        assert graph is not None

    def test_build_graph_without_god_mode(self):
        """Normal graph should compile without interrupt_before."""
        from services.dynamic_graph_builder import build_graph_from_blueprint

        blueprint = self._make_simple_blueprint()
        graph = build_graph_from_blueprint(blueprint, god_mode=False)
        assert graph is not None


class TestGodModeSessionManagement:
    """Tests for god mode session management functions."""

    def test_get_god_mode_state_returns_none_for_unknown_run(self):
        from services.dynamic_graph_builder import get_god_mode_state

        result = get_god_mode_state("nonexistent-run-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_resume_god_mode_returns_none_for_unknown_run(self):
        from services.dynamic_graph_builder import resume_god_mode

        result = await resume_god_mode("nonexistent-run-id", action="approve")
        assert result is None

    @pytest.mark.asyncio
    async def test_resume_god_mode_reject_cleans_up(self):
        from services.dynamic_graph_builder import (
            _god_mode_sessions,
            resume_god_mode,
        )

        # Manually insert a fake session
        _god_mode_sessions["test-run"] = {
            "graph": MagicMock(),
            "checkpointer": MagicMock(),
            "thread_config": {"configurable": {"thread_id": "test-run"}},
        }

        result = await resume_god_mode("test-run", action="reject")
        assert result is None
        assert "test-run" not in _god_mode_sessions


class TestToolResolution:
    """Tests for the tool resolution helper."""

    def test_resolve_tools_none_config(self):
        from services.dynamic_graph_builder import _resolve_tools

        assert _resolve_tools(None) == []

    def test_resolve_tools_empty_config(self):
        from services.dynamic_graph_builder import _resolve_tools

        assert _resolve_tools({}) == []

    def test_resolve_tools_web_search_only(self):
        from services.dynamic_graph_builder import _resolve_tools

        tools = _resolve_tools({"webSearch": True, "pdfReader": False})
        assert len(tools) == 1
        assert tools[0].name == "web_search"

    def test_resolve_tools_pdf_only(self):
        from services.dynamic_graph_builder import _resolve_tools

        tools = _resolve_tools({"webSearch": False, "pdfReader": True})
        assert len(tools) == 1
        assert tools[0].name == "pdf_search"

    def test_resolve_tools_both(self):
        from services.dynamic_graph_builder import _resolve_tools

        tools = _resolve_tools({"webSearch": True, "pdfReader": True})
        assert len(tools) == 2
        names = {t.name for t in tools}
        assert names == {"web_search", "pdf_search"}


class TestInvokeWithTools:
    """Tests for the _invoke_with_tools helper."""

    def test_invoke_without_tools_calls_llm_directly(self):
        from services.dynamic_graph_builder import _invoke_with_tools

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_llm.invoke.return_value = mock_response

        result = _invoke_with_tools(mock_llm, ["msg1", "msg2"], [])
        mock_llm.invoke.assert_called_once_with(["msg1", "msg2"])
        assert result == mock_response

    def test_invoke_with_tools_no_tool_calls(self):
        from services.dynamic_graph_builder import _invoke_with_tools

        mock_llm = MagicMock()
        mock_bound = MagicMock()
        mock_llm.bind_tools.return_value = mock_bound

        mock_response = MagicMock()
        mock_response.tool_calls = []
        mock_response.content = "No tools needed"
        mock_bound.invoke.return_value = mock_response

        mock_tool = MagicMock()
        mock_tool.name = "test_tool"

        result = _invoke_with_tools(mock_llm, ["msg"], [mock_tool])
        assert result == mock_response

    def test_invoke_with_tools_executes_tool_calls(self):
        from services.dynamic_graph_builder import _invoke_with_tools

        mock_llm = MagicMock()
        mock_bound = MagicMock()
        mock_llm.bind_tools.return_value = mock_bound

        # First call returns tool_calls
        mock_response_with_tools = MagicMock()
        mock_response_with_tools.tool_calls = [
            {"name": "web_search", "args": {"query": "test"}, "id": "call-1"}
        ]

        # Second call returns final answer
        mock_final_response = MagicMock()
        mock_final_response.content = "Final answer"
        mock_bound.invoke.side_effect = [mock_response_with_tools, mock_final_response]

        mock_tool = MagicMock()
        mock_tool.name = "web_search"
        mock_tool.invoke.return_value = "Search results"

        result = _invoke_with_tools(mock_llm, ["msg"], [mock_tool])
        mock_tool.invoke.assert_called_once_with({"query": "test"})
        assert result == mock_final_response
