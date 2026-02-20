# CLAUDE.md — CouncilOS (KI-Konzil)

This file provides context for AI assistants (Claude and others) working in this repository. Read it fully before making any changes.

---

## Project Overview

**CouncilOS** ("KI-Rat Baukasten") is a visual no-code platform for building multi-agent AI pipelines. Users compose a "council" of AI experts — each with a defined role, system prompt, LLM model, and optional tools — and connect them via a drag-and-drop canvas. The agents then collaborate in iterative loops until a document or task reaches the desired quality.

**Repository status:** This is currently a concept and architecture stage. The only file is `README.md`, which serves as the master PRD and development roadmap. No application code exists yet.

**Primary language of documentation:** German. Code, variable names, and commit messages should be in English.

---

## Planned Tech Stack

Follow these technology choices exactly — they are architectural requirements, not suggestions:

| Layer | Technology | Reason |
|---|---|---|
| AI Orchestration | **LangGraph** (Python) | Native support for cyclic graphs and `interrupt_before` (Human-in-the-Loop) |
| Backend API | **FastAPI** (Python) | WebSocket support for real-time agent status updates |
| Frontend | **React** or **Next.js** + **React Flow** | Industry standard for interactive drag-and-drop canvas UIs |
| Database | **PostgreSQL** | Stores user data and council blueprints as JSON |
| Vector DB | **ChromaDB** (local) or **Pinecone** | Powers the PDF-reader tool |
| LLMs | **Anthropic Claude 3.5 Sonnet** + **OpenAI GPT-4o** | Via API |
| Search Tool | **Tavily Search API** | For the web-search agent tool |
| PDF Tool | **PyPDF** + vector store | For the PDF-reader agent tool |

---

## Architecture Concepts

### Core Idea: Cyclic Multi-Agent Graphs

Unlike linear pipelines, CouncilOS agents run in **loops**. A critic agent can reject a draft and send it back to the master agent repeatedly until quality meets the threshold. This is the core differentiator.

### Agent Node Properties

Each agent node on the canvas has:
- **Name** — display label
- **System Prompt** — the role/persona definition
- **LLM Model** — which model to use (Claude, GPT-4o, or local)
- **Tools** — optional toggle switches: Web Search, PDF Reader

### Edge Types

- **Linear edges** — agent A always passes output to agent B
- **Conditional edges** — agent A routes dynamically (e.g. `"rework"` → back to master, `"approve"` → next stage)

### The Global State (`CouncilState`)

This is the central data structure passed between all agents in LangGraph. Always use and extend this TypedDict:

```python
from typing import TypedDict, Annotated, List
import operator

class CouncilState(TypedDict):
    input_topic: str           # The user's original prompt or uploaded PDF content
    current_draft: str         # The document currently being worked on
    feedback_history: List[str] # All critic feedback accumulated across loop iterations
    route_decision: str        # Routing signal: "rework" | "approve" | custom values
    messages: Annotated[list, operator.add]  # LLM message history (system + responses)
```

Agents should append to `feedback_history` rather than overwriting it, so the master agent can learn from all previous critique in a loop.

### Execution Modes

| Mode | Behavior |
|---|---|
| **Auto-Pilot** | Agents run fully autonomously until completion |
| **God Mode** | LangGraph pauses at each decision point via `interrupt_before`; user approves/rejects/modifies before continuing |

---

## Development Roadmap

Build in this order — **backend first, frontend second**:

### Phase 1: LangGraph Engine (Backend MVP)
- Set up Python environment and FastAPI
- Hard-code a fixed test graph: `User Input → Master AI → Critic AI → (if score < 8: back to Master; if ≥ 8: Writer AI)`
- Implement `CouncilState` and the routing logic
- Verify the loop runs correctly via terminal or Postman

### Phase 2: Visual Builder (Frontend MVP)
- Set up React + React Flow
- Build custom node components with editable name, system prompt, model selector, and tool toggles
- Build edge drawing (linear and conditional)
- Write a **parser** that converts the React Flow graph into a structured JSON and saves it to PostgreSQL

### Phase 3: Integration (Frontend ↔ Backend)
- Make LangGraph **dynamic**: read the JSON blueprint from Phase 2 and construct the graph at runtime
- Add WebSocket events: when LangGraph enters a node, emit an event so the frontend highlights that node
- Display the final output text in the frontend

### Phase 4: Tools & God Mode (Enterprise Features)
- Integrate Tavily Search API and PyPDF + vector store as agent tools
- Assign tools to specific nodes in the frontend
- Implement Human-in-the-Loop using LangGraph's `interrupt_before`
- Build the approval UI: display the paused state, reason, and Approve / Reject / Modify buttons

---

## UI Structure

### Tab A: "Rat-Architekt" (Setup Mode)
- Infinite canvas (React Flow)
- Drag nodes from a sidebar panel onto the canvas
- Click a node → open settings panel (name, system prompt, LLM, tool toggles)
- Draw edges between nodes; mark edges as conditional where needed

### Tab B: "Konferenzzimmer" (Execution Mode)
- Text input or PDF upload to start a council run
- Auto-Pilot / God Mode toggle
- Live diagram view: active agent node pulses/glows (WebSocket-driven)
- God Mode: approval popup when the graph pauses

---

## Conventions for AI Assistants

### Language
- All **code, variable names, function names, comments, and commit messages** must be in **English**
- User-facing UI text and in-code string literals for the UI may be in German (matching the product's target audience)
- Do not translate the existing German `README.md`

### Python Code Style
- Use Python 3.11+
- Type hints are mandatory — use `TypedDict` for state classes, `Annotated` for LangGraph reducers
- Follow PEP 8; use `ruff` for linting and `black` for formatting if configured
- Keep LangGraph node functions pure where possible (single input state → output state dict)
- Name node functions descriptively: `master_agent_node`, `critic_agent_node`, `route_decision`

### FastAPI Conventions
- Use async route handlers
- Separate route definitions from business logic (use service modules)
- WebSocket endpoint for live agent status: `/ws/council/{run_id}`
- REST endpoints for CRUD on council blueprints: `/api/councils/`

### React / Frontend Conventions
- Use functional components with hooks
- React Flow nodes must be wrapped in custom components (never use raw default nodes for agent cards)
- The JSON format emitted by the parser (Phase 2) must be the canonical exchange format between frontend and backend; keep it versioned
- State management: use React context or Zustand (avoid Redux unless team decides otherwise)

### Database
- Council blueprints are stored as JSONB columns in PostgreSQL
- Include a `version` field in blueprint JSON to allow schema evolution
- Use Alembic for migrations

### Testing
- Write pytest tests for all LangGraph node functions and routing logic
- Mock LLM calls in unit tests (do not make real API calls in CI)
- Frontend: React Testing Library for component tests

### Git Workflow
- Branch naming: `feature/<short-description>`, `fix/<short-description>`
- Commit messages: imperative mood, English, e.g. `Add critic agent routing logic`
- Never commit API keys or `.env` files

### Environment Variables
When code is created, expected environment variables will include:

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
TAVILY_API_KEY=
DATABASE_URL=postgresql://...
CHROMA_PERSIST_DIR=./chroma_db
```

Create a `.env.example` file (no real values) and add `.env` to `.gitignore`.

---

## Key Design Constraints

1. **Cycles are first-class** — never flatten the graph into a DAG just to simplify code. LangGraph's cycle support is the core value proposition.
2. **State is the source of truth** — agents must not store state internally; everything passes through `CouncilState`.
3. **No hardcoded graphs in production** — Phase 1 may hard-code a test graph, but from Phase 3 onward the graph must be dynamically built from the JSON blueprint.
4. **WebSockets for real-time updates** — polling is not acceptable for agent status; use WebSocket events.
5. **Human-in-the-Loop via `interrupt_before`** — do not build a custom pause mechanism; use LangGraph's built-in support.

---

## Repository Structure (Target — Once Code Exists)

```
KI-Konzil/
├── README.md              # German PRD / project blueprint (do not modify)
├── CLAUDE.md              # This file
├── .env.example           # Template for required environment variables
├── backend/
│   ├── main.py            # FastAPI app entrypoint
│   ├── api/               # Route definitions
│   ├── services/          # Business logic, LangGraph graph builder
│   ├── agents/            # Individual agent node functions
│   ├── state.py           # CouncilState TypedDict definition
│   ├── tools/             # Web search and PDF reader tool wrappers
│   └── tests/             # pytest test suite
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── nodes/     # React Flow custom node components
│   │   │   └── edges/     # React Flow custom edge components
│   │   ├── pages/         # Page-level components / Next.js pages
│   │   ├── hooks/         # Custom React hooks (WebSocket, council API)
│   │   └── utils/         # Parser: React Flow JSON → blueprint JSON
│   └── public/
└── docker-compose.yml     # Local development environment
```

---

## Getting Started (Once Implemented)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```
