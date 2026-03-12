# Story 1.2: Backend-Python-Umgebung & Requirements

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **eine vollständige `requirements.txt` mit allen Abhängigkeiten**,
so dass ich **reproduzierbar installieren kann**.

## Acceptance Criteria

1. `pip install -r requirements.txt` installiert FastAPI, LangGraph, langchain-anthropic, langchain-openai, SQLAlchemy, alembic, chromadb, tavily-python, pypdf, pytest
2. `pytest backend/tests/` läuft durch (0 oder mehr passed, 0 failed)
3. `asyncio_mode = auto` ist in `pytest.ini` konfiguriert für async Tests
4. Alle Pakete haben gepinnte Versionen für Reproduzierbarkeit

## Tasks / Subtasks

- [x] Task 1: `requirements.txt` mit allen Abhängigkeiten erstellen (AC: 1, 4)
  - [x] Subtask 1.1: Core: fastapi, uvicorn, pydantic
  - [x] Subtask 1.2: AI: langgraph, langchain-anthropic, langchain-openai
  - [x] Subtask 1.3: DB: sqlalchemy[asyncio], asyncpg, alembic
  - [x] Subtask 1.4: Tools: chromadb, tavily-python, pypdf, langchain-text-splitters
  - [x] Subtask 1.5: Test: pytest, pytest-asyncio, httpx, aiosqlite
- [x] Task 2: `pytest.ini` mit `asyncio_mode = auto` konfigurieren (AC: 2, 3)
- [x] Task 3: `backend/__init__.py` für Package-Erkennung

## Dev Notes

- `aiosqlite` wird für In-Memory-SQLite in Tests verwendet (kein PostgreSQL in CI)
- `httpx` für async FastAPI-Test-Client (`AsyncClient`)

### Project Structure Notes

- `backend/requirements.txt`
- `backend/pytest.ini`

### References

- [Source: CLAUDE.md#Python Code Style]
- [Source: _bmad-output/planning-artifacts/architecture.md#Technische-Abhängigkeiten]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `aiosqlite` ermöglicht In-Memory-SQLite für Tests ohne laufenden PostgreSQL-Server.
- `asyncio_mode = auto` ist essentiell für pytest-asyncio-Kompatibilität mit allen async Fixtures.

### File List

- `backend/requirements.txt`
- `backend/pytest.ini`
- `backend/__init__.py`
