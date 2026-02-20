"""
CouncilState — the central data structure passed between all agents in LangGraph.

All agents must read from and write to this TypedDict. Agents must not store
state internally; everything passes through CouncilState.
"""

from typing import Annotated, List, Optional
import operator
from typing_extensions import TypedDict


class CouncilState(TypedDict):
    """
    The global state shared across all agents in a council run.

    Fields:
        input_topic:        The user's original prompt or uploaded PDF content.
        current_draft:      The document currently being worked on.
        feedback_history:   All critic feedback accumulated across loop iterations.
                            Agents append here — never overwrite.
        route_decision:     Routing signal used by conditional edges.
                            Values: "rework" | "approve" | custom strings.
        messages:           LLM message history (system prompts + responses).
                            Uses operator.add reducer so messages accumulate.
        iteration_count:    Tracks how many rework loops have occurred.
        critic_score:       The numeric score (0–10) assigned by the critic agent.
        run_id:             Unique identifier for this council run (for WebSocket events).
        active_node:        Name of the currently executing agent node (for UI updates).
    """

    input_topic: str
    current_draft: str
    feedback_history: Annotated[List[str], operator.add]
    route_decision: str
    messages: Annotated[list, operator.add]
    iteration_count: int
    critic_score: Optional[float]
    run_id: str
    active_node: str


# Approval threshold: critic score must reach this value to exit the loop
APPROVAL_THRESHOLD = 8.0

# Safety limit: maximum number of rework iterations before forcing approval
MAX_ITERATIONS = 5
