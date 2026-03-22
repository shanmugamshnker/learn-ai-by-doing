# Tool Calling Deep Dive

Learn LLM tool calling — from "why it exists" to querying a real database.

## What You'll Learn

- Why LLMs need tools (and what happens without them)
- How a tool call works — the exact request/response flow
- Why structured output is the bridge between LLM and code
- The full message protocol under the hood
- Multiple tools — how the LLM picks the right one
- Tool chaining — one tool's result feeds the next
- Connecting tools to a real PostgreSQL database
- Web search — giving the LLM access to the internet

## The Core Idea

```
User: "Find the price of Samsung Galaxy S24"

Without tools:
  User → LLM → "I think it costs around ₹70,000..." (guessing)

With tools:
  User → LLM → "I need search_product" → Your code queries DB → ₹74,999
       ← LLM ← formats the answer    ← sends result back

The LLM DECIDES which tool to use (probabilistic)
Your code EXECUTES the tool        (deterministic)
JSON is how they talk to each other (structured output)
```

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [Docker](https://www.docker.com/) (for PostgreSQL)
- A free [Groq API key](https://console.groq.com/keys)

## Quick Start

```bash
cd tool-calling-deep-dive

# Setup
cp .env.example .env              # Add your Groq API key
uv sync                           # Install dependencies
docker compose up -d              # Start PostgreSQL
uv run python seed.py             # Load product catalog into DB

# Run exercises in order
uv run python 01_without_tools.py
uv run python 02_first_tool_call.py
uv run python 03_why_structured_output.py
uv run python 04_under_the_hood.py
uv run python 05_multiple_tools.py
uv run python 06_tool_chaining.py
```

## Exercises

### 01 — Without Tools
Ask the LLM questions it can't handle: product lookups, private data, booking a cab. See it fail or hallucinate.

### 02 — First Tool Call
Same kind of question, but now the LLM has a `search_product` tool. Watch it decide to use the tool, your code executes it, and the LLM returns real data.

### 03 — Why Structured Output
Side-by-side comparison: without tools the LLM returns free text (can't parse), with tools it returns structured JSON (always parseable). This is why tool calling needs structured output.

### 04 — Under the Hood
Step through the exact messages array at every stage. See `role: "tool"`, `tool_call_id`, `finish_reason: "tool_calls"`, and how the protocol works.

### 05 — Multiple Tools
Four tools available (search, compare, availability, recommendations) plus web search. The LLM picks the right one for each question — or answers directly when no tool is needed.

### 06 — Tool Chaining
The LLM calls one tool, reads the result, then calls another. One tool's output feeds the next decision — like a manager delegating tasks in sequence.

## Project Structure

```
tool-calling-deep-dive/
├── config.py                # Central config (API keys, model, DB settings)
├── docker-compose.yml       # PostgreSQL database
├── seed.py                  # Load product catalog into DB
│
├── 01_without_tools.py      # The problem
├── 02_first_tool_call.py    # The solution
├── 03_why_structured_output.py  # Why structure matters
├── 04_under_the_hood.py     # Message protocol deep dive
├── 05_multiple_tools.py     # LLM picks the right tool
├── 06_tool_chaining.py      # Sequential tool calls
│
└── tools/
    ├── catalog.py           # Product tools (connected to PostgreSQL)
    └── web_search.py        # Internet search (DuckDuckGo, no API key needed)
```

## How It Works

```
┌──────────┐     ┌───────────┐     ┌─────────────────┐
│   User   │────→│    LLM    │────→│   Your Code     │
│          │     │  (Groq)   │     │  (Python tools)  │
│  Speaks  │     │  Decides  │     │  Executes        │
│ English  │     │ which tool│     │  queries DB      │
│          │←────│ to call   │←────│  returns JSON    │
└──────────┘     └───────────┘     └─────────────────┘
                      ↕                     ↕
                 JSON (structured)    PostgreSQL / Web
```

## Technologies

- **LLM**: OpenAI SDK → Groq API (`openai/gpt-oss-120b`)
- **Database**: PostgreSQL 16 (Docker)
- **Web Search**: DuckDuckGo (via `ddgs`, no API key needed)
- **Python**: 3.12+ with `uv` package manager
