"""
Graph Builder — constructs the LangGraph execution graph for council runs.

Phase 1: Hard-coded test graph:
    User Input → Master Agent → Critic Agent → (score < 8: back to Master | score ≥ 8: Writer Agent)

Phase 3 (future): This module will be extended to build graphs dynamically
from JSON blueprints stored in PostgreSQL.
"""

import asyncio
from typing import Any, Callable, Optional
from langgraph.graph import StateGraph, END

from state import CouncilState
from agents import master_agent_node, critic_agent_node, writer_agent_node


def route_after_critic(state: CouncilState) -> str:
    """
    Conditional edge function: determines next node after the critic.

    Returns:
        "master_agent" if the critic wants rework.
        "writer_agent" if the critic approves the draft.
    """
    decision = state.get("route_decision", "rework")
    if decision == "approve":
        return "writer_agent"
    return "master_agent"


def build_council_graph(
    on_node_start: Optional[Callable[[str, str], Any]] = None,
) -> StateGraph:
    """
    Build and compile the Phase 1 hard-coded council graph.

    Graph topology:
        master_agent → critic_agent → (conditional) → master_agent | writer_agent → END

    Args:
        on_node_start: Optional async callback invoked when a node begins execution.
                       Signature: (run_id: str, node_name: str) -> Any
                       Used to emit WebSocket events for real-time UI updates.

    Returns:
        A compiled LangGraph StateGraph ready for invocation.
    """
    graph = StateGraph(CouncilState)

    # Register agent nodes
    graph.add_node("master_agent", master_agent_node)
    graph.add_node("critic_agent", critic_agent_node)
    graph.add_node("writer_agent", writer_agent_node)

    # Define edges
    graph.set_entry_point("master_agent")
    graph.add_edge("master_agent", "critic_agent")

    # Conditional edge: critic decides whether to rework or approve
    graph.add_conditional_edges(
        "critic_agent",
        route_after_critic,
        {
            "master_agent": "master_agent",
            "writer_agent": "writer_agent",
        },
    )

    # Writer is the terminal node
    graph.add_edge("writer_agent", END)

    return graph.compile()


def create_initial_state(
    input_topic: str,
    run_id: str,
) -> CouncilState:
    """
    Create a fresh CouncilState for a new council run.

    Args:
        input_topic: The user's prompt or document content.
        run_id:      Unique identifier for this run (used in WebSocket events).

    Returns:
        An initialized CouncilState dict.
    """
    return CouncilState(
        input_topic=input_topic,
        current_draft="",
        feedback_history=[],
        route_decision="",
        messages=[],
        iteration_count=0,
        critic_score=None,
        run_id=run_id,
        active_node="",
    )


async def run_council_async(
    input_topic: str,
    run_id: str,
    on_node_event: Optional[Callable[[str, str], Any]] = None,
) -> CouncilState:
    """
    Execute a full council run asynchronously.

    Args:
        input_topic:   The user's prompt.
        run_id:        Unique identifier for this run.
        on_node_event: Optional callback for WebSocket node events.

    Returns:
        The final CouncilState after the writer agent completes.
    """
    graph = build_council_graph(on_node_start=on_node_event)
    initial_state = create_initial_state(input_topic, run_id)

    # LangGraph's invoke is synchronous — run it in a thread pool to avoid
    # blocking the FastAPI event loop
    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(
        None,
        lambda: graph.invoke(initial_state),
    )

    return final_state
