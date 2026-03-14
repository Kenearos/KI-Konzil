# CouncilOS Documentation Index

**Type:** Multi-Part Full-Stack Web Application
**Primary Languages:** Python (Backend), TypeScript (Frontend)
**Architecture:** LangGraph Cyclic Multi-Agent Pipeline + React Flow Visual Builder
**Last Updated:** 2026-03-13

## Project Overview

CouncilOS ("KI-Rat Baukasten") ist eine visuelle No-Code-Plattform zum Erstellen und Ausführen von Multi-Agenten-KI-Pipelines. Nutzer bauen per Drag & Drop einen "KI-Rat" aus spezialisierten Agenten, die in zyklischen Schleifen iterativ zusammenarbeiten, bis die gewünschte Ergebnisqualität erreicht ist.

## Project Structure

Dieses Projekt besteht aus 2 Hauptteilen:

### Backend (api)

- **Type:** FastAPI REST/WebSocket API + LangGraph AI Engine
- **Location:** `backend/`
- **Tech Stack:** Python 3.11+, FastAPI, LangGraph, SQLAlchemy (async), PostgreSQL, ChromaDB
- **Entry Point:** `backend/main.py`

### Frontend (ui)

- **Type:** Next.js Single-Page Application mit React Flow Canvas
- **Location:** `frontend/`
- **Tech Stack:** Next.js 16, React, React Flow (@xyflow/react), Zustand, TypeScript
- **Entry Point:** `frontend/app/page.tsx`

## Cross-Part Integration

- Frontend kommuniziert mit Backend via REST API (`/api/councils/*`, `/api/runs/*`) und WebSocket (`/ws/council/{run_id}`)
- Blueprint-JSON ist das kanonische Austauschformat zwischen Frontend und Backend
- WebSocket-Events steuern die Echtzeit-Visualisierung des aktiven Agent-Nodes im Frontend

## Quick Reference

### Backend Quick Ref

- **Stack:** FastAPI, LangGraph, SQLAlchemy, PostgreSQL, ChromaDB
- **Entry:** `backend/main.py`
- **Pattern:** Service Layer → Agent Nodes → LangGraph StateGraph

### Frontend Quick Ref

- **Stack:** Next.js, React Flow, Zustand, TypeScript
- **Entry:** `frontend/app/page.tsx`
- **Pattern:** React Flow Canvas → Blueprint Parser → API Client

## Generated Documentation

### Core Documentation

- [Project Overview](./project-overview.md) — Executive Summary und High-Level-Architektur
- [Source Tree Analysis](./source-tree-analysis.md) — Annotierte Verzeichnisstruktur

### Existing Documentation

- [Test Coverage Analysis](./test-coverage-analysis.md) — Testabdeckung und QA-Analyse

### BMAD Planning Artifacts

- [Product Brief](../_bmad-output/planning-artifacts/product-brief.md) — Produkt-Vision und Scope
- [PRD](../_bmad-output/planning-artifacts/prd.md) — Product Requirements Document
- [Architecture](../_bmad-output/planning-artifacts/architecture.md) — Technische Architektur
- [UX Design](../_bmad-output/planning-artifacts/ux-design.md) — UX-Spezifikation
- [Epics & Stories](../_bmad-output/planning-artifacts/epics.md) — Epic- und Story-Breakdown
- [Implementation Readiness](../_bmad-output/planning-artifacts/implementation-readiness.md) — Implementierungs-Assessment
- [PRD Validation Report](../_bmad-output/planning-artifacts/prd-validation-report.md) — PRD-Qualitätsprüfung
- [Project Context](../_bmad-output/planning-artifacts/project-context.md) — AI-Kontext-Regeln

### BMAD Implementation Artifacts

- [Sprint Status](../_bmad-output/implementation-artifacts/sprint-status.yaml) — Aktueller Sprint-Stand
- [Epic 1 Retrospective](../_bmad-output/implementation-artifacts/epic-1-retro-2026-03-12.md) — Projekt-Setup & Infrastruktur
- [Epic 2 Retrospective](../_bmad-output/implementation-artifacts/epic-2-retro-2026-03-12.md) — LangGraph Engine Backend
- [Epic 3 Retrospective](../_bmad-output/implementation-artifacts/epic-3-retro-2026-03-12.md) — Visueller Baukasten Frontend
- [Epic 4 Retrospective](../_bmad-output/implementation-artifacts/epic-4-retro-2026-03-12.md) — Frontend-Backend-Integration
- [Epic 5 Retrospective](../_bmad-output/implementation-artifacts/epic-5-retro-2026-03-12.md) — Tools & God Mode
- [QA E2E Tests](../_bmad-output/implementation-artifacts/qa-e2e-tests.md) — End-to-End-Testplan

## Getting Started

### Backend Setup

**Prerequisites:** Python 3.11+, PostgreSQL 16 (oder Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

**Prerequisites:** Node.js 18+

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose (empfohlen)

**Prerequisites:** Docker, Docker Compose

```bash
cp .env.example .env
# API-Keys in .env eintragen
docker compose up -d
```

### Tests ausführen

```bash
# Backend (pytest)
cd backend && pytest tests/ -v

# Frontend (vitest)
cd frontend && npm test
```

## For AI-Assisted Development

This documentation was generated specifically to enable AI agents to understand and extend this codebase.

### When Planning New Features:

**UI-only features:**
→ Reference: `_bmad-output/planning-artifacts/architecture.md`, `frontend/app/components/`

**API/Backend features:**
→ Reference: `_bmad-output/planning-artifacts/architecture.md`, `backend/api/`, `backend/services/`

**Full-stack features:**
→ Reference: All architecture docs + `CLAUDE.md` for conventions

**New Agent Tools:**
→ Reference: `backend/tools/`, Factory-Pattern in `backend/services/dynamic_graph_builder.py`

**Deployment changes:**
→ Reference: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`

---

_Documentation generated by BMAD Method `document-project` workflow_
