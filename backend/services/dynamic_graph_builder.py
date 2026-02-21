"""
Dynamic Graph Builder — constructs LangGraph graphs from JSON blueprints.

This is the Phase 3 replacement for the hard-coded graph in graph_builder.py.
It reads a CouncilBlueprint JSON (as produced by the frontend parser) and
dynamically constructs the LangGraph StateGraph with the correct nodes,
edges, and conditional routing.
"""

import asyncio
import os
from typing import Any, Callable, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from state import CouncilState, APPROVAL_THRESHOLD, MAX_ITERATIONS


# ---------------------------------------------------------------------------
# LLM factory — maps model names from the frontend to LangChain chat models
# ---------------------------------------------------------------------------

_MODEL_MAP = {
    "claude-3-5-sonnet": lambda: ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        temperature=0.7,
        max_tokens=4096,
    ),
    "gpt-4o": lambda: ChatOpenAI(
        model="gpt-4o",
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0.7,
        max_tokens=4096,
    ),
}


def _get_llm(model_name: str) -> Any:
    """Instantiate a LangChain chat model by frontend model name."""
    factory = _MODEL_MAP.get(model_name)
    if factory is None:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Supported models: {list(_MODEL_MAP.keys())}"
        )
    return factory()


# ---------------------------------------------------------------------------
# Generic agent node factory
# ---------------------------------------------------------------------------

def _make_agent_node(
    node_id: str,
    label: str,
    system_prompt: str,
    model_name: str,
) -> Callable[[CouncilState], dict]:
    """
    Create a LangGraph node function for a user-defined agent.

    Each node function reads the CouncilState, calls the configured LLM
    with the agent's system prompt, and returns updated state fields.

    Args:
        node_id:       Unique node ID from the blueprint.
        label:         Display name of the agent (used in prompts).
        system_prompt: The persona / role definition for this agent.
        model_name:    Which LLM to use ("claude-3-5-sonnet" | "gpt-4o").

    Returns:
        A callable (CouncilState) -> dict suitable for StateGraph.add_node().
    """

    def agent_node(state: CouncilState) -> dict:
        llm = _get_llm(model_name)

        # Build user prompt from current state
        if not state["current_draft"]:
            user_content = (
                f"Please work on the following topic:\n\n{state['input_topic']}"
            )
        elif state["feedback_history"]:
            feedback_block = "\n\n---\n".join(
                f"Feedback round {i + 1}:\n{fb}"
                for i, fb in enumerate(state["feedback_history"])
            )
            user_content = (
                f"Topic: {state['input_topic']}\n\n"
                f"Current draft:\n{state['current_draft']}\n\n"
                f"Feedback ({len(state['feedback_history'])} round(s)):\n\n"
                f"{feedback_block}\n\n"
                f"Please produce an improved version."
            )
        else:
            user_content = (
                f"Topic: {state['input_topic']}\n\n"
                f"Current draft:\n{state['current_draft']}\n\n"
                f"Please review and improve this draft."
            )

        system_msg = SystemMessage(content=system_prompt)
        user_msg = HumanMessage(content=user_content)
        response = llm.invoke([system_msg, user_msg])

        return {
            "current_draft": response.content,
            "messages": [system_msg, user_msg, response],
            "active_node": node_id,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    agent_node.__name__ = f"agent_{node_id}"
    return agent_node


# ---------------------------------------------------------------------------
# Conditional routing
# ---------------------------------------------------------------------------

def _make_conditional_router(
    source_id: str,
    conditional_edges: List[Dict[str, str]],
    linear_target: Optional[str],
) -> Callable[[CouncilState], str]:
    """
    Build a conditional routing function for edges originating from source_id.

    This looks at `route_decision` in the state and maps it to the correct
    target node ID using the condition labels from the blueprint edges.

    Args:
        source_id:         The node that has outgoing conditional edges.
        conditional_edges: List of {"target": node_id, "condition": "..."}.
        linear_target:     Fallback target if no condition matches (from linear edges).

    Returns:
        A function (CouncilState) -> str returning the next node ID.
    """
    condition_map = {e["condition"]: e["target"] for e in conditional_edges}

    def router(state: CouncilState) -> str:
        decision = state.get("route_decision", "")
        if decision in condition_map:
            return condition_map[decision]
        # If there's a linear fallback, use it
        if linear_target:
            return linear_target
        # Default: return first conditional target as fallback
        if conditional_edges:
            return conditional_edges[0]["target"]
        return END

    router.__name__ = f"route_from_{source_id}"
    return router


# ---------------------------------------------------------------------------
# Critic-style node detection and creation
# ---------------------------------------------------------------------------

_CRITIC_KEYWORDS = {"critic", "kritik", "bewert", "evaluat", "review", "score"}


def _is_critic_like(system_prompt: str) -> bool:
    """Heuristic: does this agent's prompt suggest it's a critic/evaluator?"""
    lower = system_prompt.lower()
    return any(kw in lower for kw in _CRITIC_KEYWORDS)


def _make_critic_node(
    node_id: str,
    label: str,
    system_prompt: str,
    model_name: str,
) -> Callable[[CouncilState], dict]:
    """
    Create a critic-style node that scores and routes.

    This node evaluates the current draft and sets route_decision
    to "approve" or "rework" based on the score.
    """
    import re

    critic_system = (
        system_prompt + "\n\n"
        "IMPORTANT: You must respond in EXACTLY this format:\n\n"
        "SCORE: <integer 0-10>\n"
        "VERDICT: <\"approve\" if score >= 8, otherwise \"rework\">\n"
        "FEEDBACK:\n"
        "<detailed, actionable feedback>\n\n"
        "Scoring: 0-3 poor, 4-6 adequate, 7 good, 8-9 high quality, 10 exceptional."
    )

    def critic_node(state: CouncilState) -> dict:
        # Safety valve
        if state.get("iteration_count", 0) >= MAX_ITERATIONS:
            return {
                "route_decision": "approve",
                "critic_score": APPROVAL_THRESHOLD,
                "feedback_history": [
                    f"[Auto-approved after {MAX_ITERATIONS} iterations]"
                ],
                "messages": [],
                "active_node": node_id,
            }

        llm = _get_llm(model_name)

        system_msg = SystemMessage(content=critic_system)
        user_msg = HumanMessage(
            content=(
                f"Evaluate this draft on the topic '{state['input_topic']}':\n\n"
                f"{state['current_draft']}"
            )
        )

        response = llm.invoke([system_msg, user_msg])

        # Parse structured response
        score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", response.content)
        feedback_match = re.search(r"FEEDBACK:\s*(.*)", response.content, re.DOTALL)

        score = float(score_match.group(1)) if score_match else 0.0
        score = max(0.0, min(10.0, score))
        feedback = feedback_match.group(1).strip() if feedback_match else response.content.strip()

        route_decision = "approve" if score >= APPROVAL_THRESHOLD else "rework"

        result: dict = {
            "critic_score": score,
            "route_decision": route_decision,
            "messages": [system_msg, user_msg, response],
            "active_node": node_id,
        }

        if route_decision == "rework":
            result["feedback_history"] = [f"Score: {score}/10\n{feedback}"]

        return result

    critic_node.__name__ = f"critic_{node_id}"
    return critic_node


# ---------------------------------------------------------------------------
# Main: build graph from blueprint JSON
# ---------------------------------------------------------------------------

def build_graph_from_blueprint(blueprint: dict) -> Any:
    """
    Dynamically construct a compiled LangGraph from a CouncilBlueprint JSON.

    Args:
        blueprint: A dict matching the CouncilBlueprint schema:
            {
                "version": 1,
                "name": "...",
                "nodes": [{"id", "label", "systemPrompt", "model", "tools", "position"}],
                "edges": [{"id", "source", "target", "type", "condition?"}]
            }

    Returns:
        A compiled LangGraph StateGraph ready for invocation.

    Raises:
        ValueError: If the blueprint is invalid (no nodes, no entry point, etc.)
    """
    nodes = blueprint.get("nodes", [])
    edges = blueprint.get("edges", [])

    if not nodes:
        raise ValueError("Blueprint has no nodes.")

    # Build node lookup
    node_lookup = {n["id"]: n for n in nodes}

    # Find entry point: the node that has no incoming edges
    targets = {e["target"] for e in edges}
    entry_candidates = [n["id"] for n in nodes if n["id"] not in targets]
    if not entry_candidates:
        # All nodes have incoming edges (pure cycle) — use first node
        entry_candidates = [nodes[0]["id"]]
    entry_node_id = entry_candidates[0]

    # Find terminal nodes: nodes that have no outgoing edges
    sources = {e["source"] for e in edges}
    terminal_nodes = {n["id"] for n in nodes if n["id"] not in sources}

    # Build the StateGraph
    graph = StateGraph(CouncilState)

    # Register all nodes
    for node in nodes:
        nid = node["id"]
        label = node.get("label", nid)
        system_prompt = node.get("systemPrompt", f"You are {label}.")
        model_name = node.get("model", "claude-3-5-sonnet")

        if _is_critic_like(system_prompt):
            node_fn = _make_critic_node(nid, label, system_prompt, model_name)
        else:
            node_fn = _make_agent_node(nid, label, system_prompt, model_name)

        graph.add_node(nid, node_fn)

    # Set entry point
    graph.set_entry_point(entry_node_id)

    # Group edges by source
    edges_by_source: Dict[str, Dict[str, list]] = {}
    for edge in edges:
        src = edge["source"]
        if src not in edges_by_source:
            edges_by_source[src] = {"linear": [], "conditional": []}
        if edge.get("type") == "conditional":
            edges_by_source[src]["conditional"].append(edge)
        else:
            edges_by_source[src]["linear"].append(edge)

    # Add edges
    for source_id, grouped in edges_by_source.items():
        linear = grouped["linear"]
        conditional = grouped["conditional"]

        if conditional:
            # Build conditional routing
            linear_target = linear[0]["target"] if linear else None
            router = _make_conditional_router(source_id, conditional, linear_target)

            # Build the mapping dict for add_conditional_edges
            route_map: Dict[str, str] = {}
            for ce in conditional:
                route_map[ce["target"]] = ce["target"]
            if linear_target:
                route_map[linear_target] = linear_target

            graph.add_conditional_edges(source_id, router, route_map)
        elif linear:
            # Simple linear edge (only one target expected)
            graph.add_edge(source_id, linear[0]["target"])

    # Terminal nodes → END
    for tid in terminal_nodes:
        if tid not in edges_by_source:
            graph.add_edge(tid, END)

    return graph.compile()


async def run_blueprint_council_async(
    blueprint: dict,
    input_topic: str,
    run_id: str,
    on_node_event: Optional[Callable[[str, str], Any]] = None,
) -> CouncilState:
    """
    Execute a council run using a dynamically built graph from a blueprint.

    Args:
        blueprint:     The CouncilBlueprint JSON dict.
        input_topic:   The user's prompt.
        run_id:        Unique identifier for this run.
        on_node_event: Optional callback for WebSocket node events.

    Returns:
        The final CouncilState after execution completes.
    """
    compiled_graph = build_graph_from_blueprint(blueprint)

    initial_state = CouncilState(
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

    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(
        None,
        lambda: compiled_graph.invoke(initial_state),
    )

    return final_state
