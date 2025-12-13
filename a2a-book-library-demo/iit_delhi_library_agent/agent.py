"""
IIT Delhi Library Agent - FastAPI with AI-Powered Search
=========================================================
Uses OpenAI to understand natural language queries and search the catalog.

Run: python -m iit_delhi_library_agent.agent
Server: http://localhost:8003
"""

import os
import sys
import uuid
import json
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
import uvicorn

from iit_delhi_library_agent.catalog import (
    search_books, check_availability, get_all_genres,
    get_books_by_genre, get_available_books, get_catalog_stats,
    BOOKS
)


# =============================================================================
# CONFIGURATION
# =============================================================================

LIBRARY_NAME = "IIT Delhi Central Library"
PORT = 8003
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# OpenAI client
openai_client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


# =============================================================================
# AI TOOLS DEFINITION
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_catalog",
            "description": "Search for books in the library catalog by title, author, or genre keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term - can be book title, author name, genre, or topic"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_book_availability",
            "description": "Check if a specific book is available for borrowing",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the book to check"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Get book recommendations, optionally filtered by genre",
            "parameters": {
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Optional genre to filter recommendations (e.g., 'Electronics', 'Computer Science', 'Mathematics')"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_genres",
            "description": "List all available book genres in the library",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_library_stats",
            "description": "Get statistics about the library catalog (total books, available copies, etc.)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# =============================================================================
# TOOL EXECUTION
# =============================================================================

def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool and return the result."""

    if name == "search_catalog":
        query = arguments.get("query", "")
        results = search_books(query)
        if not results:
            return f"No books found matching '{query}' in {LIBRARY_NAME}."

        response = f"Found {len(results)} book(s) at {LIBRARY_NAME}:\n"
        for book in results:
            status = "Available" if book["available_copies"] > 0 else "All copies checked out"
            response += f"\n- '{book['title']}' by {book['author']} ({book['year']})"
            response += f"\n  Genre: {book['genre']} | {status} ({book['available_copies']}/{book['total_copies']} copies)"
        return response

    elif name == "check_book_availability":
        title = arguments.get("title", "")
        result = check_availability(title=title)
        if not result["found"]:
            return f"Book '{title}' not found in {LIBRARY_NAME} catalog."
        if result["available"]:
            return f"'{result['title']}' is AVAILABLE at {LIBRARY_NAME}! We have {result['available_copies']} of {result['total_copies']} copies."
        else:
            return f"'{result['title']}' is NOT available at {LIBRARY_NAME}. All {result['total_copies']} copies are checked out."

    elif name == "get_recommendations":
        genre = arguments.get("genre", "")
        if genre:
            books = get_books_by_genre(genre)
            available = [b for b in books if b["available_copies"] > 0]
        else:
            available = get_available_books()

        if not available:
            return f"No recommendations available{' for ' + genre if genre else ''} at {LIBRARY_NAME}."

        books_to_show = available[:3]
        response = f"Recommendations{' for ' + genre if genre else ''} from {LIBRARY_NAME}:\n"
        for book in books_to_show:
            response += f"\n- '{book['title']}' by {book['author']}: {book['description']}"
        return response

    elif name == "list_genres":
        genres = get_all_genres()
        return f"Genres available at {LIBRARY_NAME}: {', '.join(sorted(genres))}"

    elif name == "get_library_stats":
        stats = get_catalog_stats()
        return f"{LIBRARY_NAME} Statistics:\n- Total titles: {stats['total_titles']}\n- Total copies: {stats['total_copies']}\n- Available: {stats['available_copies']}\n- Genres: {', '.join(stats['genres'])}"

    return f"Unknown tool: {name}"


# =============================================================================
# AI PROCESSING
# =============================================================================

async def process_with_ai(user_query: str) -> str:
    """Process user query using AI with function calling."""

    messages = [
        {
            "role": "system",
            "content": f"""You are a helpful librarian at {LIBRARY_NAME}.
You help users find books, check availability, and get recommendations.

Our library specializes in:
- Engineering Mathematics and Physics
- Electronics and VLSI Design
- Computer Science and Programming
- Mechanical and Civil Engineering

Always use the available tools to search and respond. Be helpful and concise."""
        },
        {"role": "user", "content": user_query}
    ]

    try:
        # First API call - may request tool use
        response = await openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # Check if the model wants to use tools
        if assistant_message.tool_calls:
            messages.append(assistant_message.model_dump())

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"  [AI] Tool: {function_name}({function_args})")
                result = execute_tool(function_name, function_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Second API call - get final response
            final_response = await openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )

            return final_response.choices[0].message.content

        return assistant_message.content

    except Exception as e:
        print(f"  [AI] Error: {e}")
        # Fallback to direct search
        results = search_books(user_query)
        if results:
            response = f"Found {len(results)} book(s):\n"
            for book in results:
                response += f"- {book['title']} by {book['author']}\n"
            return response
        return f"I couldn't process your request. Try searching for specific terms like 'electronics' or 'algorithms'."


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class SearchRequest(BaseModel):
    query: str


class TextPart(BaseModel):
    type: str = "text"
    text: str


class Message(BaseModel):
    role: str
    parts: list[TextPart]


class TaskRequest(BaseModel):
    id: Optional[str] = None
    message: Message


# =============================================================================
# FASTAPI APP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print(f"  {LIBRARY_NAME} - AI-Powered Library Agent")
    print("=" * 60)
    print(f"  AI Model: {MODEL_NAME}")
    print(f"  A2A Endpoint: http://localhost:{PORT}/tasks/send")
    print(f"  Direct API: http://localhost:{PORT}/api/search")
    print(f"  Books in catalog: {len(BOOKS)}")
    print("=" * 60)
    yield
    print("Shutting down...")


app = FastAPI(
    title=LIBRARY_NAME,
    description="AI-Powered Library Agent",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/.well-known/agent.json")
async def get_agent_card():
    """A2A Discovery: Return the Agent Card."""
    return {
        "name": "IITDelhiLibraryAgent",
        "description": f"{LIBRARY_NAME} - AI-powered library assistant. {len(BOOKS)} titles available.",
        "url": f"http://localhost:{PORT}",
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "multiTurn": True
        },
        "skills": [
            {"id": "search", "name": "Book Search", "description": "Search for books using natural language"},
            {"id": "availability", "name": "Check Availability", "description": "Check if books are available"},
            {"id": "recommendations", "name": "Get Recommendations", "description": "Get book recommendations"}
        ]
    }


@app.post("/tasks/send")
async def handle_task(task_request: TaskRequest):
    """A2A Task Handler: Process with AI."""
    task_id = task_request.id or str(uuid.uuid4())

    query = ""
    if task_request.message and task_request.message.parts:
        query = task_request.message.parts[0].text

    print(f"[A2A] Query: {query}")

    # Process with AI
    response_text = await process_with_ai(query)

    return {
        "id": task_id,
        "status": {"state": "completed"},
        "messages": [
            {"role": "user", "parts": [{"type": "text", "text": query}]},
            {"role": "agent", "parts": [{"type": "text", "text": response_text}]}
        ]
    }


@app.post("/api/search")
async def direct_search(request: SearchRequest):
    """Direct API search - uses AI to understand query."""
    query = request.query
    print(f"[API] Search: {query}")

    # Process with AI
    ai_response = await process_with_ai(query)

    # Also get structured results for the UI
    # Extract potential search terms from the query
    search_terms = query.lower().split()
    all_results = []
    for term in search_terms:
        results = search_books(term)
        for r in results:
            if r not in all_results:
                all_results.append(r)

    return {
        "library": LIBRARY_NAME,
        "query": query,
        "ai_response": ai_response,
        "total": len(all_results),
        "books": all_results
    }


@app.get("/api/books")
async def get_all_books():
    """Get all books in the catalog."""
    return {
        "library": LIBRARY_NAME,
        "total": len(BOOKS),
        "books": BOOKS
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "library": LIBRARY_NAME, "ai_enabled": True}


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
