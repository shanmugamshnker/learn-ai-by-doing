"""
Web search tool — connects to the internet via DuckDuckGo.
No API key needed. Real search results.
"""

import json
from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet and return results."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r["title"],
                    "url": r["href"],
                    "snippet": r["body"],
                })
        if results:
            return json.dumps(results)
        return json.dumps({"message": "No results found"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Tool definition ---

WEB_SEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for information NOT in our product catalog. Use for news, weather, cab booking, general knowledge, or anything outside our store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5)",
                    },
                },
                "required": ["query"],
            },
        },
    }
]
