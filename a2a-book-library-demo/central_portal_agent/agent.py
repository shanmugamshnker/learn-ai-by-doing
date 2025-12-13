"""
Central Library Portal Agent - OpenAI SDK
==========================================
A2A-compliant central portal that aggregates results from multiple library agents.
Uses OpenAI SDK for intelligent query routing and response synthesis.

Run: python -m central_portal_agent.agent
Server: http://localhost:8000
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import AsyncOpenAI

from shared.models import (
    AgentCard, AgentSkill, AgentCapabilities,
    TaskRequest, TaskResponse, TaskStatus, TaskStatusState,
    Message, TextPart, TaskError
)
from shared.a2a_client import A2AClient


# =============================================================================
# CONFIGURATION
# =============================================================================

PORTAL_NAME = "Central Library Portal"
PORT = 8000
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Registry of library agents to connect to
# URLs can be overridden via environment variables for Docker
LIBRARY_AGENTS = [
    {
        "name": "IIT Delhi Library",
        "url": os.getenv("IIT_DELHI_LIBRARY_URL", "http://localhost:8003")
    },
    {
        "name": "IIT Bombay Library",
        "url": os.getenv("IIT_BOMBAY_LIBRARY_URL", "http://localhost:8004")
    },
]


# =============================================================================
# OPENAI CLIENT SETUP
# =============================================================================

openai_client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


# =============================================================================
# A2A FEDERATION FUNCTIONS
# =============================================================================

async def discover_all_agents(retries: int = 3, delay: float = 1.0) -> list[dict]:
    """Discover all registered library agents and their capabilities.

    Retries help avoid false "offline" results when an agent is still starting up.
    """
    discovered = []
    for library in LIBRARY_AGENTS:
        error: Optional[Exception] = None
        for attempt in range(retries):
            try:
                async with A2AClient(library["url"]) as client:
                    card = await client.discover()
                    discovered.append({
                        "name": card.name,
                        "description": card.description,
                        "url": library["url"],
                        "skills": [s.name for s in card.skills],
                        "status": "online"
                    })
                    break
            except Exception as exc:
                error = exc
                if attempt < retries - 1:
                    await asyncio.sleep(delay * (attempt + 1))
                else:
                    discovered.append({
                        "name": library["name"],
                        "url": library["url"],
                        "status": "offline",
                        "error": str(error)
                    })
    return discovered


async def query_library(url: str, query: str) -> dict:
    """Send a query to a specific library agent via A2A."""
    try:
        async with A2AClient(url) as client:
            await client.discover()
            response = await client.send_task(query)
            response_text = client.get_response_text(response)
            return {
                "url": url,
                "success": True,
                "response": response_text
            }
    except Exception as e:
        return {
            "url": url,
            "success": False,
            "error": str(e)
        }


async def federated_search(query: str) -> list[dict]:
    """Query all library agents in parallel and collect results."""
    tasks = [query_library(lib["url"], query) for lib in LIBRARY_AGENTS]
    results = await asyncio.gather(*tasks)
    return results


# =============================================================================
# OPENAI FUNCTION DEFINITIONS
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_all_libraries",
            "description": "Search for books across all connected Indian university libraries (IIT Delhi and IIT Bombay).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term - can be book title, author name, or genre"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability_all",
            "description": "Check if a specific book is available at IIT Delhi or IIT Bombay libraries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "book_title": {
                        "type": "string",
                        "description": "The title of the book to check"
                    }
                },
                "required": ["book_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommendations_all",
            "description": "Get book recommendations from IIT Delhi and IIT Bombay libraries, optionally filtered by genre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "Optional genre to filter recommendations (e.g., Fiction, Technology, Computer Science)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_connected_libraries",
            "description": "List all libraries connected to the Central Portal with their status and capabilities.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


async def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool and return the result."""

    if name == "search_all_libraries":
        query = arguments.get("query", "")
        results = await federated_search(query)

        response = f"Search results for '{query}' across all libraries:\n"
        response += "=" * 50 + "\n"

        for result in results:
            lib_name = next((lib["name"] for lib in LIBRARY_AGENTS if lib["url"] == result["url"]), "Unknown")
            if result["success"]:
                response += f"\n📚 {lib_name}:\n{result['response']}\n"
            else:
                response += f"\n❌ {lib_name}: Unavailable - {result.get('error', 'Unknown error')}\n"

        return response

    elif name == "check_availability_all":
        book_title = arguments.get("book_title", "")
        query = f"Is '{book_title}' available to borrow?"
        results = await federated_search(query)

        response = f"Availability check for '{book_title}':\n"
        response += "=" * 50 + "\n"

        for result in results:
            lib_name = next((lib["name"] for lib in LIBRARY_AGENTS if lib["url"] == result["url"]), "Unknown")
            if result["success"]:
                response += f"\n📚 {lib_name}:\n{result['response']}\n"
            else:
                response += f"\n❌ {lib_name}: Could not check - {result.get('error', 'Unknown error')}\n"

        return response

    elif name == "get_recommendations_all":
        genre = arguments.get("genre", "")
        query = f"Recommend me some {genre} books" if genre else "Give me some book recommendations"
        results = await federated_search(query)

        response = f"Recommendations{' for ' + genre if genre else ''} from all libraries:\n"
        response += "=" * 50 + "\n"

        for result in results:
            lib_name = next((lib["name"] for lib in LIBRARY_AGENTS if lib["url"] == result["url"]), "Unknown")
            if result["success"]:
                response += f"\n📚 {lib_name}:\n{result['response']}\n"
            else:
                response += f"\n❌ {lib_name}: Unavailable\n"

        return response

    elif name == "list_connected_libraries":
        agents = await discover_all_agents()

        response = "Connected Libraries:\n"
        response += "=" * 50 + "\n"

        for agent in agents:
            status_icon = "✅" if agent["status"] == "online" else "❌"
            response += f"\n{status_icon} {agent['name']}\n"
            response += f"   URL: {agent['url']}\n"
            response += f"   Status: {agent['status']}\n"
            if agent["status"] == "online":
                response += f"   Skills: {', '.join(agent.get('skills', []))}\n"

        return response

    return f"Unknown tool: {name}"


async def process_with_openai(user_query: str) -> str:
    """Process user query using OpenAI with function calling."""

    messages = [
        {
            "role": "system",
            "content": f"""You are the {PORTAL_NAME} assistant. You help users search for books
across multiple libraries in our federated library network.

Connected Indian university libraries:
- IIT Delhi Library (engineering, mathematics, electronics, physics)
- IIT Bombay Library (computer science, AI/ML, algorithms, quantum computing)

When users ask about books:
1. Use the appropriate tool to search across all libraries
2. Summarize the results clearly
3. Indicate which library has each book
4. If a book isn't available at one library, mention if it's at another

Always be helpful and guide users to find the books they need."""
        },
        {"role": "user", "content": user_query}
    ]

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
        # Execute all requested tools
        messages.append(assistant_message.model_dump())

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"[TOOL] Executing: {function_name}({function_args})")
            result = await execute_tool(function_name, function_args)

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


# =============================================================================
# AGENT CARD
# =============================================================================

AGENT_CARD = AgentCard(
    name="CentralLibraryPortal",
    description=f"{PORTAL_NAME} - Federated search across Indian university libraries (IIT Delhi and IIT Bombay). Find books, check availability, and get recommendations in one place.",
    url=f"http://localhost:{PORT}",
    version="1.0.0",
    provider="Indian University Library Federation",
    capabilities=AgentCapabilities(
        streaming=False,
        push_notifications=False,
        multi_turn=True
    ),
    skills=[
        AgentSkill(
            id="federated_search",
            name="Federated Search",
            description="Search for books across all connected libraries simultaneously",
            tags=["search", "federated", "multi-library"],
            examples=["Find Python books", "Search for fiction novels"]
        ),
        AgentSkill(
            id="availability_check",
            name="Check Availability",
            description="Check book availability across all libraries at once",
            tags=["availability", "borrow"],
            examples=["Is Clean Code available anywhere?", "Where can I find 1984?"]
        ),
        AgentSkill(
            id="recommendations",
            name="Get Recommendations",
            description="Get book recommendations from all connected libraries",
            tags=["recommendations"],
            examples=["Recommend CS books", "What should I read?"]
        ),
        AgentSkill(
            id="library_status",
            name="Library Status",
            description="Check status of all connected libraries",
            tags=["status", "info"],
            examples=["Which libraries are online?", "Show connected libraries"]
        ),
    ]
)


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("=" * 60)
    print(f"  {PORTAL_NAME} - A2A Federation Hub")
    print("=" * 60)
    print(f"  Framework: OpenAI SDK")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Agent Card: http://localhost:{PORT}/.well-known/agent.json")
    print(f"  Task Endpoint: http://localhost:{PORT}/tasks/send")
    print(f"  Connected Libraries: {len(LIBRARY_AGENTS)}")
    for lib in LIBRARY_AGENTS:
        print(f"    - {lib['name']}: {lib['url']}")
    print("=" * 60)

    # Check connectivity to library agents
    print("\nChecking library connections...")
    agents = await discover_all_agents()
    for agent in agents:
        status = "✅ Online" if agent["status"] == "online" else "❌ Offline"
        print(f"  {agent['name']}: {status}")
    print()

    yield
    print("Shutting down...")


app = FastAPI(
    title=PORTAL_NAME,
    description="A2A Federation Hub - Search across multiple library agents",
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

# Mount static files
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# =============================================================================
# UI API MODELS
# =============================================================================

class SearchRequest(BaseModel):
    query: str


# =============================================================================
# UI ENDPOINTS
# =============================================================================

@app.get("/")
async def serve_ui():
    """Serve the main UI."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "UI not available. Access API at /docs"}


@app.post("/api/search")
async def api_search(request: SearchRequest):
    """API endpoint for UI search - uses direct catalog API for structured results."""
    query = request.query
    print(f"[{datetime.now().strftime('%H:%M:%S')}] UI Search: {query}")

    # Query all libraries using their direct API endpoints (fast, structured JSON)
    results = await direct_catalog_search(query)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {sum(r.get('total', 0) for r in results)} books")

    return {
        "query": query,
        "libraries_queried": len(LIBRARY_AGENTS),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


async def direct_catalog_search(query: str) -> list[dict]:
    """Query all library catalogs directly via their REST API."""
    import httpx

    results = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for library in LIBRARY_AGENTS:
            try:
                # Call the direct API endpoint
                response = await client.post(
                    f"{library['url']}/api/search",
                    json={"query": query}
                )
                response.raise_for_status()
                data = response.json()

                results.append({
                    "library": library["name"],
                    "success": True,
                    "total": data.get("total", 0),
                    "books": data.get("books", [])
                })
            except Exception as e:
                print(f"[ERROR] {library['name']}: {e}")
                results.append({
                    "library": library["name"],
                    "success": False,
                    "total": 0,
                    "books": [],
                    "error": str(e)
                })

    return results


# =============================================================================
# A2A ENDPOINTS
# =============================================================================

@app.get("/.well-known/agent.json")
async def get_agent_card() -> dict:
    """A2A Discovery: Return the Agent Card."""
    return AGENT_CARD.model_dump(by_alias=True, exclude_none=True)


@app.post("/tasks/send")
async def handle_task(task_request: TaskRequest) -> dict:
    """A2A Task Handler: Process incoming tasks via federated search."""
    try:
        # Extract user message
        user_message = task_request.message.parts[0].text
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Query: {user_message}")

        # Process with OpenAI
        response_text = await process_with_openai(user_message)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Response: {response_text[:100]}...")

        # Build A2A response
        response = TaskResponse(
            id=task_request.id,
            status=TaskStatus(state=TaskStatusState.COMPLETED),
            messages=[
                task_request.message,
                Message(role="agent", parts=[TextPart(text=response_text)])
            ]
        )
        return response.model_dump(by_alias=True, exclude_none=True)

    except Exception as e:
        print(f"[ERROR] {e}")
        error_response = TaskResponse(
            id=task_request.id,
            status=TaskStatus(state=TaskStatusState.FAILED),
            error=TaskError(message=str(e))
        )
        return error_response.model_dump(by_alias=True, exclude_none=True)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    agents = await discover_all_agents()
    online_count = sum(1 for a in agents if a["status"] == "online")

    return {
        "status": "healthy",
        "agent": AGENT_CARD.name,
        "portal": PORTAL_NAME,
        "framework": "OpenAI SDK",
        "connected_libraries": len(LIBRARY_AGENTS),
        "libraries_online": online_count,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/libraries")
async def list_libraries():
    """List all connected library agents and their status."""
    return await discover_all_agents()


# =============================================================================
# INTERACTIVE CLI MODE
# =============================================================================

async def interactive_mode():
    """Run an interactive CLI session."""
    print("\n" + "=" * 60)
    print(f"  {PORTAL_NAME} - Interactive Mode")
    print("=" * 60)
    print("  Type your questions about books, or:")
    print("    'libraries' - Show connected libraries")
    print("    'quit' - Exit")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("Goodbye!")
                break

            if user_input.lower() == 'libraries':
                agents = await discover_all_agents()
                for agent in agents:
                    status = "✅" if agent["status"] == "online" else "❌"
                    print(f"  {status} {agent['name']} ({agent['url']})")
                continue

            # Process query
            print("\nSearching across all libraries...\n")
            response = await process_with_openai(user_input)
            print(f"Portal: {response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=PORTAL_NAME)
    parser.add_argument("--cli", action="store_true", help="Run in interactive CLI mode")
    args = parser.parse_args()

    if args.cli:
        asyncio.run(interactive_mode())
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=PORT)
