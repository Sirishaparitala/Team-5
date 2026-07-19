"""Tavily web search service for fetching fresh sports knowledge."""

from tavily import TavilyClient
from config import Config


def _build_query(sport: str, difficulty: str) -> str:
    """Build a targeted search query based on sport and difficulty."""
    difficulty_modifiers = {
        "easy": "basic facts and popular records",
        "medium": "statistics records and notable events",
        "hard": "obscure trivia lesser-known facts and deep statistics",
    }
    modifier = difficulty_modifiers.get(difficulty, "facts and trivia")
    return f"{sport} sports quiz trivia {modifier} 2024 2025"


def search_sports_content(sport: str, difficulty: str) -> list[dict]:
    """
    Search the web for sports-related content using Tavily.

    Returns a list of dicts with 'title', 'content', and 'url' keys.
    """
    client = TavilyClient(api_key=Config.TAVILY_API_KEY)
    query = _build_query(sport, difficulty)

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=8,
            include_answer=False,
        )

        results = []
        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", ""),
                }
            )

        print(f"[Search] Found {len(results)} results for '{query}'")
        return results

    except Exception as e:
        print(f"[Search] Error: {e}")
        return []
