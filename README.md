# Learn AI By Doing

A collection of hands-on AI learning projects. Each topic is a complete, working project that teaches core concepts through practical implementation.

## 📚 Topics

### 1. [ChromaDB Local RAG](./chromadb-local-rag)
Learn vector databases and semantic search with ChromaDB.

**What you'll learn:**
- Vector databases and embeddings
- Semantic search (meaning-based, not keyword-based)
- How text is converted to 384-dimensional vectors
- Distance metrics and similarity calculation

**Features:**
- Interactive search across 2,225 food items
- Workflow tracer showing the complete embedding process
- Real nutrition dataset with calories and categories

**Quick start:**
```bash
cd chromadb-local-rag
uv sync
uv run load_food_data.py
uv run query_foods.py
```

---

### 2. [Tool Calling Deep Dive](./tool-calling-deep-dive)
Learn LLM tool calling — from "why it exists" to querying a real database.

**What you'll learn:**
- Why LLMs need tools (and what happens without them)
- The exact request/response protocol behind tool calling
- Structured output — the bridge between LLM and code
- Multiple tools, tool chaining, and web search
- Connecting tools to a real PostgreSQL database

**Features:**
- 6 progressive exercises (run them in order)
- Real PostgreSQL database with product catalog
- Web search tool (DuckDuckGo, no API key needed)
- Interactive menus — try your own questions

**Quick start:**
```bash
cd tool-calling-deep-dive
cp .env.example .env     # Add your Groq API key
uv sync
docker compose up -d
uv run python seed.py
uv run python 01_without_tools.py
```

---

## 🚀 Getting Started

Each topic is self-contained with its own README, dependencies, and examples.

1. Choose a topic
2. Follow the README in that directory
3. Learn by doing!

## 🛠️ Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## 📖 Learning Philosophy

This repository follows a "learn by doing" approach:
- Every topic has working code you can run
- Concepts are explained through practical examples
- You can modify and experiment with the code
- Step-by-step progression from basics to advanced

---

**Happy Learning!** 🎓

If you find this helpful, give it a ⭐ on GitHub!
