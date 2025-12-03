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
