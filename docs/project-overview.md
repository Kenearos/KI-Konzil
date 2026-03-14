# CouncilOS — Project Overview

**Date:** 2026-03-13
**Type:** Multi-Part Full-Stack Web Application
**Architecture:** Cyclic Multi-Agent Pipeline (LangGraph) + Visual Graph Builder (React Flow)

## Executive Summary

CouncilOS ist eine visuelle No-Code-Plattform für zyklische Multi-Agenten-KI-Pipelines. Das Projekt besteht aus einem Python-Backend (FastAPI + LangGraph) und einem TypeScript-Frontend (Next.js + React Flow). Nutzer bauen per Drag & Drop einen "KI-Rat" aus spezialisierten Agenten, verbinden sie mit linearen und bedingten Kanten, und führen den Rat entweder autonom (Auto-Pilot) oder mit menschlicher Kontrolle (God Mode) aus.

**Kern-Differenzierung:** Im Gegensatz zu linearen KI-Pipelines unterstützt CouncilOS **echte Zyklen** — ein Kritiker-Agent kann ein Dokument wiederholt an den Master-Agent zurückweisen, bis die Qualitätsschwelle erreicht ist.

## Project Classification

- **Repository Type:** Multi-Part (Backend + Frontend)
- **Project Type(s):** AI Platform, Web Application
- **Primary Languages:** Python 3.11+, TypeScript 5.x
- **Architecture Pattern:** Service-Oriented Backend + Component-Based Frontend

## Multi-Part Structure

Dieses Projekt besteht aus 2 Hauptteilen:

### Backend (`backend/`)

- **Type:** REST/WebSocket API + AI Engine
- **Purpose:** LangGraph-basierte KI-Orchestrierung, Blueprint-Verwaltung, Run-Management
- **Tech Stack:** FastAPI, LangGraph, SQLAlchemy (async), PostgreSQL, ChromaDB, Anthropic/OpenAI APIs

### Frontend (`frontend/`)

- **Type:** Single-Page Application
- **Purpose:** Visueller Canvas zum Erstellen von Agent-Graphen, Live-Execution-Anzeige, God-Mode-UI
- **Tech Stack:** Next.js 16, React Flow (@xyflow/react), Zustand, TypeScript

### How Parts Integrate

1. **Blueprint-JSON** ist das kanonische Austauschformat — Frontend erstellt es, Backend konsumiert es
2. **REST API** (`/api/councils/*`, `/api/runs/*`) für CRUD-Operationen und Run-Management
3. **WebSocket** (`/ws/council/{run_id}`) für Echtzeit-Node-Status-Updates
4. **God-Mode-Events** (`run_paused`) triggern das Approval-Overlay im Frontend

## Technology Stack Summary

### Backend Stack

| Kategorie | Technologie | Version | Zweck |
|-----------|-------------|---------|-------|
| Web-Framework | FastAPI | ≥ 0.111 | REST + WebSocket API |
| AI-Orchestrierung | LangGraph | ≥ 0.2.0 | Zyklische Multi-Agent-Graphen |
| LLM-Provider | Anthropic Claude 3.5 Sonnet | via API | Primäres KI-Modell |
| LLM-Provider | OpenAI GPT-4o | via API | Alternatives KI-Modell |
| Datenbank | PostgreSQL 16 | Docker | Blueprint- und Run-Speicherung |
| ORM | SQLAlchemy 2.0+ (async) | asyncpg | Datenbankzugriff |
| Migrationen | Alembic | ≥ 1.13 | Schema-Evolution |
| Vektor-DB | ChromaDB | ≥ 0.5.0 | PDF-Suche (Embeddings) |
| Web-Suche | Tavily API | — | Agent-Tool |
| Tests | pytest + pytest-asyncio | ≥ 8.0 | Unit + Integration Tests |

### Frontend Stack

| Kategorie | Technologie | Version | Zweck |
|-----------|-------------|---------|-------|
| Framework | Next.js | 16.x | App Router SSR/CSR |
| Canvas-Bibliothek | React Flow (@xyflow/react) | 12+ | Drag & Drop Graph-Builder |
| State Management | Zustand | — | Canvas- und Run-State |
| Sprache | TypeScript | 5.x | Typsicherheit |
| Styling | Tailwind CSS | — | UI-Design |
| Tests | Vitest | — | Component + Unit Tests |

## Key Features

1. **Visueller Canvas (Rat-Architekt):** Drag & Drop Agent-Nodes, konfigurierbare System-Prompts, LLM-Modell-Auswahl, Tool-Toggles (Web-Suche, PDF-Reader)
2. **Lineare & Bedingte Edges:** Workflows mit Verzweigungen und Schleifen definieren
3. **Blueprint-Speicherung:** Council-Konfigurationen als JSON in PostgreSQL speichern und laden
4. **Auto-Pilot-Modus:** Agents laufen autonom bis zum Abschluss
5. **God Mode (Human-in-the-Loop):** LangGraph `interrupt_before` pausiert an jedem Node; Nutzer kann genehmigen, ablehnen oder den Draft modifizieren
6. **Echtzeit-Updates:** WebSocket-Events pulsieren den aktiven Node im Canvas
7. **Agent-Tools:** Tavily Web-Suche und PDF-Upload + ChromaDB-Suche als optionale Agent-Werkzeuge
8. **Run-Verlauf:** Alle Council-Runs mit Ergebnis, Critic-Score und Iterationszahl abrufbar

## Architecture Highlights

### LangGraph Cyclic Graph

```
Master-Agent → Critic-Agent → [Score < 8: zurück zu Master] → Writer-Agent → END
```

- **CouncilState** (TypedDict mit `operator.add`-Reducern) ist die einzige Wahrheitsquelle
- **Safety Valve:** `MAX_ITERATIONS = 5` erzwingt Genehmigung nach 5 Runden
- **Score-basiertes Routing:** Numerischer Critic-Score (nicht LLM-Verdict) bestimmt das Routing

### Dynamic Graph Builder

Ab Phase 3 werden Graphen **dynamisch** aus Blueprint-JSON gebaut — kein hartcodierter Graph in Produktion.

### Factory Pattern für Tools

`create_web_search_tool()` und `create_pdf_search_tool()` Factories geben `None` zurück wenn API-Keys fehlen — keine Crashes bei fehlender Konfiguration.

## Development Overview

### Prerequisites

- Python 3.11+ (Backend)
- Node.js 22+ (Frontend)
- Docker + Docker Compose (PostgreSQL, optionale Container)

### Getting Started

```bash
# 1. Repository klonen
git clone https://github.com/Kenearos/KI-Konzil.git
cd KI-Konzil

# 2. Umgebungsvariablen konfigurieren
cp .env.example .env
# ANTHROPIC_API_KEY, OPENAI_API_KEY, TAVILY_API_KEY eintragen

# 3. Docker Compose starten (PostgreSQL + Services)
docker compose up -d
```

### Key Commands

#### Backend

- **Install:** `pip install -r backend/requirements.txt`
- **Dev:** `cd backend && uvicorn main:app --reload`
- **Test:** `cd backend && pytest tests/ -v`

#### Frontend

- **Install:** `cd frontend && npm install`
- **Dev:** `cd frontend && npm run dev`
- **Test:** `cd frontend && npm test`

## Repository Structure

```
KI-Konzil/
├── backend/           → FastAPI + LangGraph Backend
│   ├── agents/        → Agent-Node-Funktionen (Master, Critic, Writer)
│   ├── api/           → REST/WebSocket-Routen
│   ├── services/      → Graph-Builder, Blueprint-Service, Run-Service
│   ├── models/        → SQLAlchemy ORM-Modelle
│   ├── tools/         → Web-Suche, PDF-Reader
│   ├── tests/         → 10 pytest-Testdateien (125+ Tests)
│   └── alembic/       → Datenbankmigrationen
├── frontend/          → Next.js + React Flow Frontend
│   └── app/
│       ├── components/ → Canvas, Nodes, Edges, Panels
│       ├── hooks/     → useCouncilWebSocket
│       ├── store/     → Zustand Council-Store
│       ├── utils/     → Blueprint-Parser, API-Client
│       └── __tests__/ → 4 vitest-Testdateien (26+ Tests)
├── _bmad-output/      → BMAD Planning & Implementation Artifacts
├── docs/              → Projektdokumentation
└── docker-compose.yml → Lokale Entwicklungsumgebung
```

## Quantitative Summary

| Metrik | Wert |
|--------|------|
| Backend Python-Dateien | 38 |
| Frontend TS/TSX-Dateien | 23 |
| Backend Lines of Code | ~4.567 |
| Frontend Lines of Code | ~2.070 |
| Backend-Tests | 125+ (10 Testdateien) |
| Frontend-Tests | 26+ (4 Testdateien) |
| Epics | 5 (alle abgeschlossen) |
| Stories | 18 (alle abgeschlossen) |
| API-Endpunkte | 8 REST + 1 WebSocket |
| DB-Tabellen | 2 (blueprints, council_runs) |

## Documentation Map

For detailed information, see:

- [index.md](./index.md) — Master Documentation Index
- [source-tree-analysis.md](./source-tree-analysis.md) — Annotierte Verzeichnisstruktur
- [Architecture](../_bmad-output/planning-artifacts/architecture.md) — Detaillierte Systemarchitektur
- [PRD](../_bmad-output/planning-artifacts/prd.md) — Product Requirements Document
- [CLAUDE.md](../CLAUDE.md) — AI-Konventionen und Coding-Standards

---

_Generated using BMAD Method `document-project` workflow_
