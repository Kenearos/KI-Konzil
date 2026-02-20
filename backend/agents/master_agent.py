"""
Master Agent Node — creates and refines drafts based on critic feedback.

This agent is the primary content creator. On the first iteration it produces
an initial draft. On subsequent iterations it incorporates all feedback from
the feedback_history to improve the draft.
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from state import CouncilState


_SYSTEM_PROMPT = """You are the Master AI in a council of expert AIs.
Your job is to write high-quality content on the given topic.
When you receive critic feedback, carefully incorporate ALL feedback points
and produce an improved draft. Be thorough and precise."""


def _build_master_prompt(state: CouncilState) -> str:
    """Build the user-facing prompt for the master agent based on current state."""
    if not state["feedback_history"]:
        return (
            f"Please write a comprehensive, well-structured document on the following topic:\n\n"
            f"{state['input_topic']}"
        )

    feedback_block = "\n\n---\n".join(
        f"Feedback round {i + 1}:\n{fb}"
        for i, fb in enumerate(state["feedback_history"])
    )

    return (
        f"Topic: {state['input_topic']}\n\n"
        f"Your current draft:\n{state['current_draft']}\n\n"
        f"The critic has provided the following feedback across {len(state['feedback_history'])} round(s):\n\n"
        f"{feedback_block}\n\n"
        f"Please produce an improved draft that fully addresses ALL feedback points above."
    )


def master_agent_node(state: CouncilState) -> dict:
    """
    LangGraph node function for the Master Agent.

    Reads input_topic and feedback_history from state, calls the LLM,
    and returns an updated current_draft.

    Args:
        state: The current CouncilState.

    Returns:
        A dict with updated state fields: current_draft, messages, active_node.
    """
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        temperature=0.7,
        max_tokens=2048,
    )

    system_msg = SystemMessage(content=_SYSTEM_PROMPT)
    user_msg = HumanMessage(content=_build_master_prompt(state))

    response = llm.invoke([system_msg, user_msg])
    draft = response.content

    return {
        "current_draft": draft,
        "messages": [system_msg, user_msg, response],
        "active_node": "master_agent",
        "iteration_count": state.get("iteration_count", 0) + 1,
    }
