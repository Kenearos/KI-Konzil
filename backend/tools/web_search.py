"""
Web Search Tool — Tavily Search API wrapper for agent nodes.

Provides a LangChain-compatible tool that agents can use to search the web
for current information. Requires the TAVILY_API_KEY environment variable.
"""

import os
from typing import Optional

from langchain_core.tools import tool


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for current information on a topic.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A formatted string with search results including titles, URLs, and snippets.
    """
    from tavily import TavilyClient

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "[Web Search Error] TAVILY_API_KEY environment variable is not set."

    client = TavilyClient(api_key=api_key)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
        )
    except Exception as exc:  # noqa: BLE001
        return f"[Web Search Error] {exc}"

    results = response.get("results", [])
    if not results:
        return f"No results found for: {query}"

    formatted = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "No content available")
        formatted.append(f"{i}. **{title}**\n   URL: {url}\n   {content}")

    return "\n\n".join(formatted)


def create_web_search_tool() -> Optional[tool]:
    """Factory that returns the web_search tool if Tavily is configured."""
    if os.environ.get("TAVILY_API_KEY"):
        return web_search
    return None
