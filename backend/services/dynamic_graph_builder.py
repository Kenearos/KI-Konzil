"""
Dynamic Graph Builder — constructs LangGraph graphs from JSON blueprints.

This is the Phase 3 replacement for the hard-coded graph in graph_builder.py.
It reads a CouncilBlueprint JSON (as produced by the frontend parser) and
dynamically constructs the LangGraph StateGraph with the correct nodes,
edges, and conditional routing.

Phase 4 additions:
- Tool binding: agents with tools enabled (webSearch, pdfReader) get
  LangChain tools bound to their LLM via .bind_tools().
- God Mode: supports interrupt_before for human-in-the-loop approval.
"""

import asyncio
import os
from typing import Any, Callable, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from state import CouncilState, APPROVAL_THRESHOLD, MAX_ITERATIONS
from tools.web_search import web_search
from tools.pdf_reader import pdf_search


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
# Tool resolution
# ---------------------------------------------------------------------------

def _resolve_tools(tools_config: Optional[dict]) -> list:
    """
    Resolve a node's tools config to a list of LangChain tool objects.

    Args:
        tools_config: Dict like {"webSearch": true, "pdfReader": true}

    Returns:
        A list of LangChain tool objects to bind to the LLM.
    """
    if not tools_config:
        return []

    resolved = []
    if tools_config.get("webSearch"):
        resolved.append(web_search)
    if tools_config.get("pdfReader"):
        resolved.append(pdf_search)
    return resolved


def _invoke_with_tools(llm: Any, messages: list, tools: list) -> Any:
    """
    Invoke an LLM, optionally with tools bound. If the LLM returns tool
    calls, execute them and feed results back for a final answer.

    Args:
        llm: A LangChain chat model instance.
        messages: The message list to send.
        tools: List of LangChain tools (may be empty).

    Returns:
        The final LLM response message.
    """
    if not tools:
        return llm.invoke(messages)

    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)

    # If no tool calls, return directly
    if not response.tool_calls:
        return response

    # Execute tool calls and collect results
    from langchain_core.messages import ToolMessage

    tool_map = {t.name: t for t in tools}
    tool_messages = [response]

    for tc in response.tool_calls:
        tool_fn = tool_map.get(tc["name"])
        if tool_fn:
            try:
                result = tool_fn.invoke(tc["args"])
            except Exception as exc:  # noqa: BLE001
                result = f"[Tool Error] {exc}"
        else:
            result = f"[Tool Error] Unknown tool: {tc['name']}"

        tool_messages.append(
            ToolMessage(content=str(result), tool_call_id=tc["id"])
        )

    # Final LLM call with tool results
    return llm_with_tools.invoke(messages + tool_messages)


# ---------------------------------------------------------------------------
# Generic agent node factory
# ---------------------------------------------------------------------------

def _make_agent_node(
    node_id: str,
    label: str,
    system_prompt: str,
    model_name: str,
    tools_config: Optional[dict] = None,
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
        tools_config:  Optional dict like {"webSearch": true, "pdfReader": true}.

    Returns:
        A callable (CouncilState) -> dict suitable for StateGraph.add_node().
    """
    node_tools = _resolve_tools(tools_config)

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
        response = _invoke_with_tools(llm, [system_msg, user_msg], node_tools)

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
    tools_config: Optional[dict] = None,
) -> Callable[[CouncilState], dict]:
    """
    Create a critic-style node that scores and routes.

    This node evaluates the current draft and sets route_decision
    to "approve" or "rework" based on the score.
    """
    import re

    node_tools = _resolve_tools(tools_config)

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

        response = _invoke_with_tools(llm, [system_msg, user_msg], node_tools)

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

def build_graph_from_blueprint(
    blueprint: dict,
    god_mode: bool = False,
) -> Any:
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
        god_mode: If True, compile with interrupt_before on all nodes so the
                  user can approve/reject at each step (Human-in-the-Loop).

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
    all_node_ids = []
    for node in nodes:
        nid = node["id"]
        all_node_ids.append(nid)
        label = node.get("label", nid)
        system_prompt = node.get("systemPrompt", f"You are {label}.")
        model_name = node.get("model", "claude-3-5-sonnet")
        tools_config = node.get("tools")

        if _is_critic_like(system_prompt):
            node_fn = _make_critic_node(
                nid, label, system_prompt, model_name, tools_config
            )
        else:
            node_fn = _make_agent_node(
                nid, label, system_prompt, model_name, tools_config
            )

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

    # God Mode: interrupt before every node so the user can approve/reject
    if god_mode:
        return graph.compile(interrupt_before=all_node_ids)

    return graph.compile()


async def run_blueprint_council_async(
    blueprint: dict,
    input_topic: str,
    run_id: str,
    god_mode: bool = False,
    on_node_event: Optional[Callable[[str, str], Any]] = None,
) -> CouncilState:
    """
    Execute a council run using a dynamically built graph from a blueprint.

    In auto-pilot mode, the graph runs to completion.
    In god mode, the graph pauses before each node via interrupt_before,
    allowing human approval through the resume mechanism.

    Args:
        blueprint:     The CouncilBlueprint JSON dict.
        input_topic:   The user's prompt.
        run_id:        Unique identifier for this run.
        god_mode:      If True, pause before each node for human approval.
        on_node_event: Optional callback for WebSocket node events.

    Returns:
        The final CouncilState after execution completes.
    """
    from langgraph.checkpoint.memory import MemorySaver

    if god_mode:
        checkpointer = MemorySaver()
        nodes_list = blueprint.get("nodes", [])
        all_node_ids = [n["id"] for n in nodes_list]
        compiled_graph = _build_graph_with_checkpointer(
            blueprint, checkpointer, all_node_ids
        )

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

        thread_config = {"configurable": {"thread_id": run_id}}

        loop = asyncio.get_event_loop()
        state = await loop.run_in_executor(
            None,
            lambda: compiled_graph.invoke(initial_state, config=thread_config),
        )

        # Store the graph and checkpointer for later resume
        _god_mode_sessions[run_id] = {
            "graph": compiled_graph,
            "checkpointer": checkpointer,
            "thread_config": thread_config,
        }

        return state

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


# ---------------------------------------------------------------------------
# God Mode session management
# ---------------------------------------------------------------------------

# In-memory store for active god mode sessions (graph + checkpointer)
_god_mode_sessions: Dict[str, dict] = {}


def _build_graph_with_checkpointer(
    blueprint: dict,
    checkpointer: Any,
    interrupt_node_ids: List[str],
) -> Any:
    """Build a compiled graph with a checkpointer for god mode."""
    nodes = blueprint.get("nodes", [])
    edges = blueprint.get("edges", [])

    if not nodes:
        raise ValueError("Blueprint has no nodes.")

    node_lookup = {n["id"]: n for n in nodes}
    targets = {e["target"] for e in edges}
    entry_candidates = [n["id"] for n in nodes if n["id"] not in targets]
    if not entry_candidates:
        entry_candidates = [nodes[0]["id"]]
    entry_node_id = entry_candidates[0]

    sources = {e["source"] for e in edges}
    terminal_nodes = {n["id"] for n in nodes if n["id"] not in sources}

    graph = StateGraph(CouncilState)

    for node in nodes:
        nid = node["id"]
        label = node.get("label", nid)
        system_prompt = node.get("systemPrompt", f"You are {label}.")
        model_name = node.get("model", "claude-3-5-sonnet")
        tools_config = node.get("tools")

        if _is_critic_like(system_prompt):
            node_fn = _make_critic_node(
                nid, label, system_prompt, model_name, tools_config
            )
        else:
            node_fn = _make_agent_node(
                nid, label, system_prompt, model_name, tools_config
            )

        graph.add_node(nid, node_fn)

    graph.set_entry_point(entry_node_id)

    edges_by_source: Dict[str, Dict[str, list]] = {}
    for edge in edges:
        src = edge["source"]
        if src not in edges_by_source:
            edges_by_source[src] = {"linear": [], "conditional": []}
        if edge.get("type") == "conditional":
            edges_by_source[src]["conditional"].append(edge)
        else:
            edges_by_source[src]["linear"].append(edge)

    for source_id, grouped in edges_by_source.items():
        linear = grouped["linear"]
        conditional = grouped["conditional"]

        if conditional:
            linear_target = linear[0]["target"] if linear else None
            router = _make_conditional_router(source_id, conditional, linear_target)
            route_map: Dict[str, str] = {}
            for ce in conditional:
                route_map[ce["target"]] = ce["target"]
            if linear_target:
                route_map[linear_target] = linear_target
            graph.add_conditional_edges(source_id, router, route_map)
        elif linear:
            graph.add_edge(source_id, linear[0]["target"])

    for tid in terminal_nodes:
        if tid not in edges_by_source:
            graph.add_edge(tid, END)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_node_ids,
    )


async def resume_god_mode(
    run_id: str,
    action: str = "approve",
    modified_state: Optional[dict] = None,
) -> Optional[CouncilState]:
    """
    Resume a paused god mode run after human approval.

    Args:
        run_id:         The run ID of the paused session.
        action:         "approve" to continue, "reject" to stop.
        modified_state: Optional partial state override (for "modify" action).

    Returns:
        The next CouncilState (may be another interrupt or final).
        None if the run_id is not found.
    """
    session = _god_mode_sessions.get(run_id)
    if not session:
        return None

    if action == "reject":
        _god_mode_sessions.pop(run_id, None)
        return None

    compiled_graph = session["graph"]
    thread_config = session["thread_config"]

    if modified_state:
        compiled_graph.update_state(thread_config, modified_state)

    loop = asyncio.get_event_loop()
    state = await loop.run_in_executor(
        None,
        lambda: compiled_graph.invoke(None, config=thread_config),
    )

    # If state indicates completion, clean up
    if state and state.get("route_decision") == "done":
        _god_mode_sessions.pop(run_id, None)

    return state


def get_god_mode_state(run_id: str) -> Optional[dict]:
    """Get the current state of a paused god mode session."""
    session = _god_mode_sessions.get(run_id)
    if not session:
        return None

    graph = session["graph"]
    thread_config = session["thread_config"]
    snapshot = graph.get_state(thread_config)

    return {
        "run_id": run_id,
        "paused": bool(snapshot.next),
        "next_nodes": list(snapshot.next) if snapshot.next else [],
        "current_state": dict(snapshot.values) if snapshot.values else {},
    }
