"""
Writer Agent Node — final polishing of an approved draft.

This agent receives a critic-approved draft and produces the final,
publication-ready version with polished formatting and language.
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from state import CouncilState


_SYSTEM_PROMPT = """You are the Writer AI in a council of expert AIs.
You receive a draft that has already been approved for quality by the Critic AI.
Your job is to give it a final professional polish:

- Improve sentence flow and readability
- Ensure consistent formatting (headers, bullet points, paragraphs)
- Fix any grammatical or stylistic issues
- Do NOT change the factual content or overall structure
- Preserve all key information from the draft

Return only the polished document — no meta-commentary."""


def writer_agent_node(state: CouncilState) -> dict:
    """
    LangGraph node function for the Writer Agent.

    Receives the approved current_draft and returns a polished final version.

    Args:
        state: The current CouncilState.

    Returns:
        A dict with the final polished current_draft and updated messages.
    """
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        temperature=0.4,
        max_tokens=4096,
    )

    system_msg = SystemMessage(content=_SYSTEM_PROMPT)
    user_msg = HumanMessage(
        content=(
            f"Please give a final professional polish to this approved document "
            f"on the topic '{state['input_topic']}':\n\n"
            f"{state['current_draft']}"
        )
    )

    response = llm.invoke([system_msg, user_msg])

    return {
        "current_draft": response.content,
        "messages": [system_msg, user_msg, response],
        "active_node": "writer_agent",
        "route_decision": "done",
    }
