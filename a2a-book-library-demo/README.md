# A2A Federated Library System

A production-grade demonstration of **Google's Agent-to-Agent (A2A) Protocol** for multi-library search federation.

## Use Case

> "Our state has many libraries going through digital transformation. Each library maintains their own catalog system. We need a central portal where customers can search ALL libraries at once."

## Key Features

| Feature | Description |
|---------|-------------|
| **A2A Protocol** | Full implementation of Google's Agent-to-Agent protocol |
| **AI-Powered Search** | Natural language queries processed by OpenAI |
| **Federated Search** | Query multiple libraries simultaneously |
| **Interactive UI** | Visual flow demonstration of A2A communication |
| **Docker Ready** | One command to run the entire system |

## Project Structure

```
a2a-book-library-demo/
├── shared/                          # Shared utilities
│   ├── __init__.py
│   ├── models.py                    # A2A Pydantic models
│   └── a2a_client.py                # A2A client for federation
│
├── iit_delhi_library_agent/         # IIT Delhi Library
│   ├── __init__.py
│   ├── catalog.py                   # 12 books: Engineering, Math, Physics
│   └── agent.py                     # FastAPI + OpenAI
│
├── iit_bombay_library_agent/        # IIT Bombay Library
│   ├── __init__.py
│   ├── catalog.py                   # 12 books: CS, AI/ML, Quantum
│   └── agent.py                     # FastAPI + OpenAI
│
├── central_portal_agent/            # Central Portal
│   ├── __init__.py
│   ├── agent.py                     # Federated search orchestrator
│   └── static/                      # Web UI
│       ├── index.html
│       ├── styles.css
│       └── app.js
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start with Docker (Recommended)

### 1. Configure Environment

```bash
cd a2a-book-library-demo
cp .env.example .env
```

Edit `.env` and add your API key:
```env
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

This starts all services:
- **IIT Delhi Library**: http://localhost:8003
- **IIT Bombay Library**: http://localhost:8004
- **Central Portal**: http://localhost:8000

### 3. Open the Web UI

Visit http://localhost:8000 to see the interactive A2A flow visualization.

### 4. Test the API

```bash
# Check agent cards
curl http://localhost:8003/.well-known/agent.json | jq
curl http://localhost:8004/.well-known/agent.json | jq

# Check central portal health
curl http://localhost:8000/health | jq

# List connected libraries
curl http://localhost:8000/libraries | jq
```

### 5. Stop the System

```bash
docker-compose down
```

---

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
cd a2a-book-library-demo
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 3. Start the Agents (3 terminals)

**Terminal 1 - IIT Delhi Library:**
```bash
python -m iit_delhi_library_agent.agent
# Running on http://localhost:8003
```

**Terminal 2 - IIT Bombay Library:**
```bash
python -m iit_bombay_library_agent.agent
# Running on http://localhost:8004
```

**Terminal 3 - Central Portal:**
```bash
python -m central_portal_agent.agent
# Running on http://localhost:8000
```

## Usage

### Web UI

Open http://localhost:8000 in your browser. The UI shows:
- Real-time A2A flow visualization
- Step-by-step query processing
- Results from both libraries

### Interactive CLI Mode

```bash
python -m central_portal_agent.agent --cli
```

### Example Session

```
You: Find books about machine learning

Portal: Searching across all libraries...

IIT Delhi Library:
Found 1 book(s):
- 'Machine Learning' by Tom Mitchell (1997)
  Genre: Artificial Intelligence | Available (2/5 copies)

IIT Bombay Library:
Found 3 book(s):
- 'Deep Learning' by Ian Goodfellow (2016)
  Genre: Artificial Intelligence | Available (5/12 copies)
- 'Pattern Recognition and Machine Learning' by Christopher Bishop (2006)
  Genre: Artificial Intelligence | Available (3/8 copies)
- 'Reinforcement Learning' by Richard Sutton (2018)
  Genre: Artificial Intelligence | Available (2/6 copies)

You: Is the CLRS algorithms book available?

Portal:
IIT Bombay Library:
'Introduction to Algorithms' is AVAILABLE! We have 10 of 20 copies.
```

## A2A Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/agent.json` | GET | A2A Discovery - Agent Card |
| `/tasks/send` | POST | A2A Task Handler |
| `/api/search` | POST | Direct search API |
| `/health` | GET | Health check |

## Book Catalogs

### IIT Delhi Library (12 books)
- Engineering Mathematics, Digital Electronics, Signals and Systems
- Data Structures, Thermodynamics, Strength of Materials
- Control Systems, Electrodynamics, Microprocessors
- Compiler Design, Machine Learning, VLSI Design

### IIT Bombay Library (12 books)
- Introduction to Algorithms (CLRS), Deep Learning, Pattern Recognition
- Computer Organization, AI: A Modern Approach, Database Systems
- Computer Networks, Reinforcement Learning, Operating Systems
- NLP with Python, Quantum Computing, Speech & Language Processing

## Extending the Demo

1. **Add more libraries** - Create new agent folders following the pattern
2. **Add real databases** - Replace in-memory catalogs with PostgreSQL/MongoDB
3. **Add authentication** - Implement A2A auth schemes
4. **Deploy to cloud** - Use Docker Compose / Kubernetes

## References

- [A2A Protocol Specification](https://a2a-protocol.org)
- [Google A2A Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
