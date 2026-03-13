# Story 5.4: Run-Verlauf (History)

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **vergangene Council-Runs einsehen**,
so dass ich **Ergebnisse nachträglich nachschlagen kann**.

## Acceptance Criteria

1. `GET /api/runs/` → paginierte Liste aller Runs (neueste zuerst)
2. `GET /api/runs/{run_id}` → `status`, `final_draft`, `critic_score`, `iteration_count`, `input_topic`
3. Unbekannte `run_id` → `404 Not Found`
4. Abgeschlossene Runs werden in PostgreSQL persistiert (`council_runs`-Tabelle)
5. `?skip=0&limit=20` Query-Parameter für Paginierung

## Tasks / Subtasks

- [x] Task 1: `services/run_service.py` (AC: 1–4)
  - [x] Subtask 1.1: `create_run()`, `get_run()`, `list_runs(skip, limit)`
  - [x] Subtask 1.2: `update_run_completed()`, `update_run_failed()`
- [x] Task 2: `api/run_history_routes.py` REST-Endpunkte (AC: 1–3, 5)
  - [x] Subtask 2.1: `RunHistoryResponse` Pydantic-Modell
  - [x] Subtask 2.2: `GET /runs/` und `GET /runs/{run_id}`
- [x] Task 3: Run nach Abschluss in DB persistieren
  - [x] Subtask 3.1: `create_run()` beim Start (in `routes.py`)
  - [x] Subtask 3.2: `update_run_completed()` nach Graph-Abschluss
- [x] Task 4: Unit-Tests (AC: 1–5)

## Dev Notes

- `run_history_router` unter `/api`-Prefix eingehangen
- DB-Persistierung: `create_run()` bei `POST /run` → `update_run_completed()` nach Fertigstellung
- `list_runs()` nutzt `ORDER BY created_at DESC` für neueste-zuerst Sortierung

### Project Structure Notes

- `backend/services/run_service.py`
- `backend/api/run_history_routes.py`
- `backend/tests/test_run_service.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Datenbankschema — council_runs]
- [Source: _bmad-output/planning-artifacts/prd.md#FR-02.7]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `run_history_router` ist von `routes.py` getrennt, da Council-Runs und Run-History konzeptionell verschiedene Ressourcen sind.
- Tests nutzen `AsyncSession` mit In-Memory-SQLite (`aiosqlite`).

### File List

- `backend/services/run_service.py`
- `backend/api/run_history_routes.py`
- `backend/tests/test_run_service.py`
