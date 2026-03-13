# Story 1.3: Datenbank-Migrationen mit Alembic

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **Alembic-Migrationen für `blueprints` und `council_runs`**,
so dass ich **das Datenbankschema versioniert verwalten kann**.

## Acceptance Criteria

1. `alembic upgrade head` erstellt Tabellen `blueprints` und `council_runs`
2. `alembic current` zeigt die aktuelle Revision
3. `blueprints`-Tabelle hat: `id` (UUID), `version` (Int), `name`, `nodes` (JSON), `edges` (JSON), `created_at`, `updated_at`
4. `council_runs`-Tabelle hat: `id`, `blueprint_id` (nullable FK), `input_topic`, `status`, `final_draft`, `critic_score`, `iteration_count`, `created_at`, `completed_at`
5. SQLAlchemy async ORM-Modelle existieren für beide Tabellen

## Tasks / Subtasks

- [x] Task 1: Alembic-Konfiguration initialisieren (AC: 1, 2)
  - [x] Subtask 1.1: `alembic.ini` mit `script_location` konfigurieren
  - [x] Subtask 1.2: `alembic/env.py` für async SQLAlchemy anpassen
- [x] Task 2: Migration 001 — `blueprints`-Tabelle (AC: 3)
- [x] Task 3: Migration 002 — `council_runs`-Tabelle (AC: 4)
- [x] Task 4: SQLAlchemy ORM-Modelle (AC: 5)
  - [x] Subtask 4.1: `models/blueprint.py`
  - [x] Subtask 4.2: `models/council_run.py`
- [x] Task 5: `database.py` mit async Engine und Session-Fabrik

## Dev Notes

- Async SQLAlchemy mit `asyncpg` für PostgreSQL, `aiosqlite` für Tests
- `get_session()` als FastAPI-Dependency für Dependency Injection
- In Tests: `AsyncEngine` mit In-Memory-SQLite, `create_all()` statt Alembic

### Project Structure Notes

- `backend/alembic/versions/001_create_blueprints_table.py`
- `backend/alembic/versions/002_create_council_runs_table.py`
- `backend/models/blueprint.py`
- `backend/models/council_run.py`
- `backend/database.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Datenbankschema]
- [Source: CLAUDE.md#Database — Alembic for migrations]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- Alembic `env.py` wurde für async Engine (run_async_migrations) angepasst.
- ORM-Modelle nutzen `String(36)` für UUIDs (portabel zwischen PostgreSQL und SQLite).

### File List

- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/versions/001_create_blueprints_table.py`
- `backend/alembic/versions/002_create_council_runs_table.py`
- `backend/models/__init__.py`
- `backend/models/blueprint.py`
- `backend/models/council_run.py`
- `backend/database.py`
