# Story 2.6: FastAPI-Run-Endpunkte implementieren

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **API-Nutzer**,
möchte ich **`POST /api/councils/run` und `GET /api/councils/run/{run_id}`**,
so dass ich **einen Council-Run starten und sein Ergebnis abrufen kann**.

## Acceptance Criteria

1. `POST /api/councils/run` → `202 Accepted` mit `run_id`, asynchroner Hintergrundausführung
2. `GET /api/councils/run/{run_id}` → `status`, `final_draft` bei abgeschlossenem Run
3. Unbekannte `run_id` → `404 Not Found`
4. Leeres `input_topic` → Validierungsfehler (422)
5. `GET /api/health` → `{"status": "ok", "service": "CouncilOS API"}`
6. FastAPI-App registriert alle Router unter `/api`-Prefix

## Tasks / Subtasks

- [x] Task 1: `api/routes.py` mit Run-Endpunkten (AC: 1–4)
  - [x] Subtask 1.1: `CouncilRunRequest` Pydantic-Modell
  - [x] Subtask 1.2: `POST /councils/run` mit `BackgroundTasks`
  - [x] Subtask 1.3: `GET /councils/run/{run_id}` mit `run_store.get()`
  - [x] Subtask 1.4: `GET /health` (AC: 5)
- [x] Task 2: `api/run_store.py` In-Memory-Run-Store (AC: 2, 3)
- [x] Task 3: `main.py` FastAPI-Entrypoint (AC: 6)
  - [x] Subtask 3.1: Router-Registrierung mit `/api` Prefix
  - [x] Subtask 3.2: CORS-Middleware
- [x] Task 4: Unit-Tests für alle Endpunkte (AC: 1–5)

## Dev Notes

- `BackgroundTasks.add_task()` für nicht-blockierende LangGraph-Ausführung
- `run_store.create(run_id, input_topic)` → status: "pending"
- Test-Setup: `AsyncClient(app=app)` via `httpx` ohne echten LangGraph-Lauf

### Project Structure Notes

- `backend/api/routes.py`
- `backend/api/run_store.py`
- `backend/main.py`
- `backend/tests/test_api.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#REST-Endpunkte]
- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-002]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `run_store` ist ein einfaches `dict` mit Thread-Safe-Operationen (GIL ausreichend für MVP).
- `BackgroundTasks` erlaubt sofortige `202`-Antwort ohne auf LangGraph zu warten.
- CORS: `allow_origins=["*"]` für lokale Entwicklung; in Produktion einschränken.

### File List

- `backend/api/__init__.py`
- `backend/api/routes.py`
- `backend/api/run_store.py`
- `backend/main.py`
- `backend/tests/test_api.py`
