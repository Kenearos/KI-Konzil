"""
Critic Agent Node — evaluates the current draft and decides whether to approve or rework.

The critic scores the draft from 0–10 and returns structured feedback.
If the score meets APPROVAL_THRESHOLD, route_decision is set to "approve".
Otherwise it is set to "rework" and the feedback is appended to feedback_history.
"""

import os
import re
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from state import CouncilState, APPROVAL_THRESHOLD, MAX_ITERATIONS


_SYSTEM_PROMPT = """You are the Critic AI in a council of expert AIs.
Your job is to rigorously evaluate the quality of a draft document.

You must respond in EXACTLY this format — no deviations:

SCORE: <integer 0-10>
VERDICT: <"approve" if score >= 8, otherwise "rework">
FEEDBACK:
<detailed, actionable feedback explaining what must be improved>

Scoring criteria:
- 0–3: Poor structure, major factual gaps, incoherent
- 4–6: Adequate but needs significant improvement
- 7:   Good but has notable weaknesses
- 8–9: High quality, minor improvements possible
- 10:  Exceptional, publication-ready

Be strict. Only award 8+ if the document genuinely meets high quality standards."""


def _parse_critic_response(content: str) -> tuple[float, str, str]:
    """
    Parse the structured critic response.

    Returns:
        (score, verdict, feedback) tuple.
        Falls back to ("rework", full content) on parse failure.
    """
    score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", content)
    verdict_match = re.search(r"VERDICT:\s*(approve|rework)", content, re.IGNORECASE)
    feedback_match = re.search(r"FEEDBACK:\s*(.*)", content, re.DOTALL)

    score = float(score_match.group(1)) if score_match else 0.0
    verdict = verdict_match.group(1).lower() if verdict_match else "rework"
    feedback = feedback_match.group(1).strip() if feedback_match else content.strip()

    # Clamp score to 0–10
    score = max(0.0, min(10.0, score))

    return score, verdict, feedback


def critic_agent_node(state: CouncilState) -> dict:
    """
    LangGraph node function for the Critic Agent.

    Reads current_draft from state, evaluates it, and returns:
    - route_decision: "approve" or "rework"
    - critic_score: numeric score
    - feedback_history: appended with new feedback (if rework)
    - active_node: "critic_agent"

    Safety valve: if iteration_count >= MAX_ITERATIONS, force approval
    to prevent infinite loops.

    Args:
        state: The current CouncilState.

    Returns:
        A dict with updated state fields.
    """
    # Safety valve: prevent infinite loops
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        return {
            "route_decision": "approve",
            "critic_score": APPROVAL_THRESHOLD,
            "feedback_history": [
                f"[Auto-approved after {MAX_ITERATIONS} iterations]"
            ],
            "messages": [],
            "active_node": "critic_agent",
        }

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        temperature=0.2,  # Low temperature for consistent evaluation
        max_tokens=1024,
    )

    system_msg = SystemMessage(content=_SYSTEM_PROMPT)
    user_msg = HumanMessage(
        content=(
            f"Please evaluate this draft on the topic '{state['input_topic']}':\n\n"
            f"{state['current_draft']}"
        )
    )

    response = llm.invoke([system_msg, user_msg])
    score, verdict, feedback = _parse_critic_response(response.content)

    # Override verdict based on threshold to ensure consistency
    if score >= APPROVAL_THRESHOLD:
        route_decision = "approve"
    else:
        route_decision = "rework"

    result: dict = {
        "critic_score": score,
        "route_decision": route_decision,
        "messages": [system_msg, user_msg, response],
        "active_node": "critic_agent",
    }

    # Only append feedback if we're sending back for rework
    if route_decision == "rework":
        result["feedback_history"] = [
            f"Score: {score}/10\n{feedback}"
        ]

    return result
