# CouncilOS — Source Tree Analysis

**Date:** 2026-03-13

## Overview

CouncilOS ist ein Multi-Part Full-Stack-Projekt mit klar getrenntem Python-Backend und TypeScript-Frontend. Die Verzeichnisstruktur folgt etablierten Konventionen für FastAPI (Backend) und Next.js App Router (Frontend).

## Multi-Part Structure

Dieses Projekt ist in 2 Hauptteile organisiert:

- **Backend** (`backend/`): FastAPI REST/WebSocket API + LangGraph AI Engine
- **Frontend** (`frontend/`): Next.js App mit React Flow Canvas

## Complete Directory Structure

```
KI-Konzil/
├── .claude/commands/              # BMAD Claude Code Skill-Definitionen (42 Dateien)
├── .env.example                   # Template für Umgebungsvariablen
├── .gitignore                     # Git-Ausschlüsse (.env, node_modules, __pycache__, etc.)
├── CLAUDE.md                      # AI-Konventionen und Projekt-Kontext
├── README.md                      # Deutsche Projektbeschreibung (Ursprungs-PRD)
│
├── _bmad/                         # BMAD Method v6 Installation
│   ├── _config/                   # Agent-Manifeste, Tool-Manifeste
│   ├── _memory/                   # Agent-Erinnerungen
│   ├── bmm/                       # Business Method Module
│   │   ├── agents/                # Agent-Definitionen (analyst, architect, dev, pm, qa, sm, ux)
│   │   ├── config.yaml            # Modul-Konfiguration (Sprache: Deutsch)
│   │   ├── data/                  # PRD-Vorlagen, Projekt-Templates
│   │   ├── teams/                 # Team-Kompositionen
│   │   └── workflows/             # BMAD-Workflow-Definitionen
│   │       ├── 1-analysis/        # Product Brief, Research
│   │       ├── 2-plan-workflows/  # PRD, UX Design
│   │       ├── 3-solutioning/     # Architecture, Epics, Implementation Readiness
│   │       ├── 4-implementation/  # Sprint Planning, Stories, Dev, Code Review, Retro
│   │       ├── document-project/  # Projekt-Dokumentation (dieses Dokument)
│   │       ├── generate-project-context/  # AI-Kontext generieren
│   │       ├── qa-generate-e2e-tests/     # QA Test-Generierung
│   │       └── bmad-quick-flow/   # Quick Spec + Dev Workflow
│   └── core/                      # BMAD Core (Tasks, Workflows, Agents)
│
├── _bmad-output/                  # BMAD generierte Artefakte
│   ├── planning-artifacts/        # Product Brief, PRD, Architecture, UX, Epics
│   │   ├── product-brief.md       # ← Analyst Agent (Mary)
│   │   ├── prd.md                 # ← PM Agent (John)
│   │   ├── prd-validation-report.md  # ← PRD Validation
│   │   ├── architecture.md        # ← Architect Agent (Winston)
│   │   ├── ux-design.md           # ← UX Designer Agent
│   │   ├── epics.md               # ← PM Agent (John)
│   │   ├── implementation-readiness.md  # ← Architect Agent (Winston)
│   │   └── project-context.md     # ← Generate Project Context
│   └── implementation-artifacts/  # Sprint Status, Stories, Retros
│       ├── sprint-status.yaml     # Sprint-Tracking (alle 5 Epics: done)
│       ├── stories/               # 20 Story-Dateien (alle: done)
│       ├── epic-1-retro-*.md      # Retrospektive Epic 1
│       ├── epic-2-retro-*.md      # Retrospektive Epic 2
│       ├── epic-3-retro-*.md      # Retrospektive Epic 3
│       ├── epic-4-retro-*.md      # Retrospektive Epic 4
│       ├── epic-5-retro-*.md      # Retrospektive Epic 5
│       └── qa-e2e-tests.md        # E2E-Testplan
│
├── backend/                       # ★ Python FastAPI Backend
│   ├── Dockerfile                 # Python 3.11 + Uvicorn
│   ├── main.py                    # ★ FastAPI App Entrypoint
│   ├── state.py                   # ★ CouncilState TypedDict + Konstanten
│   ├── database.py                # Async SQLAlchemy Engine + Session Factory
│   ├── requirements.txt           # Python-Abhängigkeiten
│   ├── pytest.ini                 # pytest-Konfiguration (asyncio_mode=auto)
│   │
│   ├── agents/                    # ★ LangGraph Agent-Node-Funktionen
│   │   ├── __init__.py
│   │   ├── master_agent.py        # Master-Agent: erstellt/überarbeitet Drafts
│   │   ├── critic_agent.py        # Critic-Agent: bewertet Drafts (Score 0-10)
│   │   └── writer_agent.py        # Writer-Agent: formatiert finalen Output
│   │
│   ├── api/                       # FastAPI Route-Definitionen
│   │   ├── __init__.py
│   │   ├── routes.py              # Council Run: POST /api/councils/run, GET .../run/{id}
│   │   ├── blueprint_routes.py    # Blueprint CRUD: /api/councils/
│   │   ├── run_history_routes.py  # Run History: GET /api/runs/
│   │   ├── run_store.py           # In-Memory Run Store (Thread-safe)
│   │   └── websocket.py           # WS /ws/council/{run_id} — Echtzeit-Events
│   │
│   ├── services/                  # Business-Logik
│   │   ├── __init__.py
│   │   ├── graph_builder.py       # Phase 1: Hartcodierter LangGraph-Graph
│   │   ├── dynamic_graph_builder.py  # ★ Phase 3+: Dynamischer Graph aus Blueprint-JSON
│   │   ├── blueprint_service.py   # Blueprint-CRUD via SQLAlchemy
│   │   └── run_service.py         # Run-CRUD via SQLAlchemy
│   │
│   ├── models/                    # SQLAlchemy ORM-Modelle
│   │   ├── __init__.py
│   │   ├── blueprint.py           # Blueprint-Tabelle (UUID, JSONB nodes/edges)
│   │   └── council_run.py         # CouncilRun-Tabelle (Status, Draft, Score)
│   │
│   ├── tools/                     # Agent-Tools
│   │   ├── __init__.py
│   │   ├── web_search.py          # Tavily Web-Suche + Factory-Funktion
│   │   └── pdf_reader.py          # PyPDF + ChromaDB + Factory-Funktion
│   │
│   ├── alembic/                   # Datenbankmigrationen
│   │   ├── alembic.ini            # Alembic-Konfiguration
│   │   ├── env.py                 # Async Migration-Environment
│   │   ├── script.py.mako         # Migration-Template
│   │   └── versions/
│   │       ├── 001_create_blueprints_table.py
│   │       └── 002_create_council_runs_table.py
│   │
│   └── tests/                     # ★ pytest Test-Suite (125+ Tests)
│       ├── __init__.py
│       ├── test_state.py          # CouncilState-Validierung (9 Tests)
│       ├── test_routing.py        # Critic-Parsing + Routing-Logik (21 Tests)
│       ├── test_run_store.py      # In-Memory Store CRUD (10 Tests)
│       ├── test_api.py            # REST-Endpunkte (20+ Tests)
│       ├── test_blueprint_api.py  # Blueprint-CRUD API
│       ├── test_blueprint_service.py  # Blueprint-Service (20+ Tests)
│       ├── test_run_service.py    # Run-Service (15+ Tests)
│       ├── test_dynamic_graph_builder.py  # Dynamischer Graph-Builder
│       ├── test_god_mode.py       # God Mode / Human-in-the-Loop
│       └── test_tools.py          # Web-Suche + PDF-Reader
│
├── frontend/                      # ★ Next.js + React Flow Frontend
│   ├── Dockerfile                 # Node.js 22 Multi-Stage Build
│   ├── .dockerignore
│   ├── .gitignore
│   ├── README.md                  # Frontend-README
│   ├── package.json               # Dependencies + Scripts
│   ├── package-lock.json
│   ├── next.config.ts             # Next.js-Konfiguration
│   ├── tsconfig.json              # TypeScript-Konfiguration
│   ├── eslint.config.mjs          # ESLint-Konfiguration
│   ├── postcss.config.mjs         # PostCSS (Tailwind)
│   ├── vitest.config.ts           # Vitest Test-Konfiguration
│   │
│   ├── app/                       # ★ Next.js App Router
│   │   ├── page.tsx               # Landing Page (Redirect)
│   │   ├── layout.tsx             # Root Layout + Navigation
│   │   ├── globals.css            # Globale Styles (Tailwind)
│   │   ├── favicon.ico
│   │   │
│   │   ├── rat-architekt/         # Tab A: Visueller Canvas
│   │   │   └── page.tsx           # ArchitectCanvas-Seite
│   │   │
│   │   ├── konferenzzimmer/       # Tab B: Live-Execution
│   │   │   └── page.tsx           # Konferenzzimmer-Seite
│   │   │
│   │   ├── components/            # React-Komponenten
│   │   │   ├── ArchitectCanvas.tsx  # ★ Haupt-Canvas (React Flow)
│   │   │   ├── NavTabs.tsx        # Tab-Navigation
│   │   │   ├── nodes/             # Custom React Flow Node-Komponenten
│   │   │   ├── edges/             # Custom React Flow Edge-Komponenten
│   │   │   └── panels/           # Settings-Panels (Node, Edge, God Mode)
│   │   │
│   │   ├── hooks/                 # Custom React Hooks
│   │   │   └── useCouncilWebSocket.ts  # WebSocket-Hook für Live-Updates
│   │   │
│   │   ├── store/                 # Zustand State Management
│   │   │   └── council-store.ts   # Globaler Council-Store
│   │   │
│   │   ├── types/                 # TypeScript-Typen
│   │   │   └── council.ts         # AgentNodeData, BlueprintNode, etc.
│   │   │
│   │   ├── utils/                 # Utility-Funktionen
│   │   │   ├── blueprint-parser.ts  # parseGraphToBlueprint()
│   │   │   └── api-client.ts      # REST API Client
│   │   │
│   │   └── __tests__/             # ★ Vitest Tests (26+ Tests)
│   │       ├── blueprint-parser.test.ts
│   │       ├── council-store.test.ts
│   │       ├── api-client.test.ts
│   │       └── types.test.ts
│   │
│   └── public/                    # Statische Assets
│       ├── file.svg, globe.svg, next.svg, vercel.svg, window.svg
│
├── docs/                          # Projektdokumentation
│   ├── index.md                   # ★ Dokumentations-Index
│   ├── project-overview.md        # ★ Projekt-Übersicht
│   ├── source-tree-analysis.md    # ★ Dieses Dokument
│   └── test-coverage-analysis.md  # QA Testabdeckungs-Analyse
│
└── docker-compose.yml             # ★ Lokale Dev-Umgebung (db + api + frontend)
```

## Critical Directories

### `backend/agents/`

Enthält die drei Kern-Agent-Node-Funktionen, die im LangGraph-Graphen als Nodes registriert werden.

**Purpose:** KI-Agent-Logik (Prompt-Engineering, LLM-Aufrufe, State-Updates)
**Contains:** `master_agent.py`, `critic_agent.py`, `writer_agent.py`
**Entry Points:** Jede Datei exportiert eine `*_agent_node(state: CouncilState)` Funktion
**Integration:** Wird von `services/graph_builder.py` und `services/dynamic_graph_builder.py` importiert

### `backend/services/`

Business-Logik-Schicht zwischen API und Datenbank/LangGraph.

**Purpose:** Graph-Konstruktion, Blueprint-CRUD, Run-Management
**Contains:** `graph_builder.py` (Phase 1), `dynamic_graph_builder.py` (Phase 3+), `blueprint_service.py`, `run_service.py`
**Entry Points:** `build_council_graph()`, `build_graph_from_blueprint()`, `run_council_async()`
**Integration:** API-Routen rufen Services auf; Services rufen Agents und DB auf

### `backend/api/`

FastAPI-Route-Definitionen (REST + WebSocket).

**Purpose:** HTTP-Endpunkte und WebSocket-Verbindungen
**Contains:** `routes.py`, `blueprint_routes.py`, `run_history_routes.py`, `websocket.py`, `run_store.py`
**Entry Points:** Registriert als Router in `main.py`

### `backend/tools/`

Optional aktivierbare Agent-Werkzeuge.

**Purpose:** Web-Suche (Tavily) und PDF-Reader (ChromaDB) als LangChain-Tools
**Contains:** `web_search.py`, `pdf_reader.py`
**Integration:** Via Factory-Pattern (`create_web_search_tool()`, `create_pdf_search_tool()`) in `dynamic_graph_builder.py`

### `frontend/app/components/`

React-Komponenten für Canvas, Nodes, Edges und Panels.

**Purpose:** Visuelle Darstellung des Agent-Graphen
**Contains:** `ArchitectCanvas.tsx`, `NavTabs.tsx`, `nodes/`, `edges/`, `panels/`
**Integration:** Verwendet React Flow Custom Nodes/Edges, Zustand-Store

### `frontend/app/utils/`

Reine Utility-Funktionen ohne Side-Effects.

**Purpose:** Blueprint-Parser (Canvas → JSON) und API-Client (REST-Aufrufe)
**Contains:** `blueprint-parser.ts`, `api-client.ts`
**Integration:** Vom Zustand-Store und den Komponenten aufgerufen

## Entry Points

### Backend

- **Main Entry:** `backend/main.py` — FastAPI-App mit CORS, Routen, Health-Check
- **Bootstrap:** `uvicorn main:app --reload` oder Docker

### Frontend

- **Main Entry:** `frontend/app/page.tsx` — Redirect zu `/rat-architekt`
- **Bootstrap:** `npm run dev` oder Docker

## File Organization Patterns

### Backend (Python)

| Pattern | Purpose | Beispiele |
|---------|---------|-----------|
| `agents/*_agent.py` | LangGraph-Node-Funktionen | `master_agent.py`, `critic_agent.py` |
| `api/*_routes.py` | FastAPI-Router | `blueprint_routes.py`, `run_history_routes.py` |
| `services/*_service.py` | Business-Logik | `blueprint_service.py`, `run_service.py` |
| `models/*.py` | SQLAlchemy ORM-Modelle | `blueprint.py`, `council_run.py` |
| `tests/test_*.py` | pytest-Tests | `test_routing.py`, `test_api.py` |

### Frontend (TypeScript)

| Pattern | Purpose | Beispiele |
|---------|---------|-----------|
| `components/*.tsx` | React-Komponenten | `ArchitectCanvas.tsx`, `NavTabs.tsx` |
| `components/nodes/*.tsx` | Custom React Flow Nodes | Agent-Node-Typen |
| `components/edges/*.tsx` | Custom React Flow Edges | Linear, Conditional |
| `hooks/use*.ts` | Custom React Hooks | `useCouncilWebSocket.ts` |
| `store/*-store.ts` | Zustand-Stores | `council-store.ts` |
| `utils/*.ts` | Reine Utility-Funktionen | `blueprint-parser.ts`, `api-client.ts` |
| `__tests__/*.test.ts` | Vitest-Tests | `blueprint-parser.test.ts` |

## Configuration Files

| Datei | Beschreibung |
|-------|-------------|
| `.env.example` | Template für API-Keys und DB-URL |
| `.gitignore` | Git-Ausschlüsse |
| `CLAUDE.md` | AI-Konventionen und Projekt-Kontext |
| `docker-compose.yml` | Docker-Service-Orchestrierung (db, api, frontend) |
| `backend/requirements.txt` | Python-Abhängigkeiten |
| `backend/pytest.ini` | pytest-Konfiguration (`asyncio_mode = auto`) |
| `backend/alembic/alembic.ini` | Alembic-Migrations-Konfiguration |
| `frontend/package.json` | Node.js-Abhängigkeiten und Scripts |
| `frontend/tsconfig.json` | TypeScript-Kompiler-Konfiguration |
| `frontend/next.config.ts` | Next.js-Konfiguration |
| `frontend/eslint.config.mjs` | ESLint-Regeln |
| `frontend/vitest.config.ts` | Vitest-Test-Konfiguration |
| `_bmad/bmm/config.yaml` | BMAD-Modul-Konfiguration (Sprache: Deutsch) |

## Notes for Development

- **Backend-Tests** laufen ohne Docker — SQLite in-memory wird für alle Tests verwendet
- **Frontend-Tests** laufen ohne Backend — API-Calls werden in Tests gemockt
- **Keine echten LLM-Aufrufe** in CI/Tests — alle Agent-Tests verwenden gemockte LLMs
- **TypedDict `CouncilState`** ist die einzige Wahrheitsquelle — Agents speichern keinen internen Zustand
- **Factory-Pattern für Tools** — `create_web_search_tool()` / `create_pdf_search_tool()` geben `None` zurück wenn API-Keys fehlen
- **Blueprint-JSON** ist das kanonische Format — Frontend erstellt es, Backend konsumiert es

---

_Generated using BMAD Method `document-project` workflow_
