# Story 3.4: Blueprint CRUD — Frontend & Backend

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **Councils speichern, laden und löschen können**,
so dass ich **meine Konfigurationen wiederverwenden kann**.

## Acceptance Criteria

1. `POST /api/councils/` mit Blueprint → `201 Created` + gespeichertes Blueprint mit `id`
2. `GET /api/councils/` → Liste aller Blueprints
3. `GET /api/councils/{id}` → Einzelnes Blueprint; unbekannte ID → `404`
4. `PUT /api/councils/{id}` → Aktualisiertes Blueprint
5. `DELETE /api/councils/{id}` → `204 No Content`; unbekannte ID → `404`
6. Frontend: „Speichern"-Button ruft `councilApi.create()` auf, Bestätigung erscheint
7. Frontend: Blueprint-Export als JSON-Datei

## Tasks / Subtasks

- [x] Task 1: `api/blueprint_routes.py` mit CRUD-Endpunkten (AC: 1–5)
  - [x] Subtask 1.1: Pydantic-Request/Response-Modelle
  - [x] Subtask 1.2: Alle fünf CRUD-Endpunkte mit DB-Session
- [x] Task 2: `services/blueprint_service.py` Service-Layer (AC: 1–5)
  - [x] Subtask 2.1: `create_blueprint()`, `get_blueprint()`, `list_blueprints()`
  - [x] Subtask 2.2: `update_blueprint()`, `delete_blueprint()`
- [x] Task 3: Frontend `utils/api-client.ts` Blueprint-Client (AC: 6)
- [x] Task 4: Speichern/Export-Buttons in `rat-architekt/page.tsx` (AC: 6, 7)
- [x] Task 5: Unit-Tests für Service und API (AC: 1–5)

## Dev Notes

- Service-Layer nutzt `AsyncSession` von SQLAlchemy
- Tests: In-Memory SQLite, `create_all()` statt Alembic
- Frontend: `URL.createObjectURL()` für JSON-Download ohne Server

### Project Structure Notes

- `backend/api/blueprint_routes.py`
- `backend/services/blueprint_service.py`
- `backend/tests/test_blueprint_api.py`
- `backend/tests/test_blueprint_service.py`
- `frontend/app/utils/api-client.ts`
- `frontend/app/rat-architekt/page.tsx`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#REST-Endpunkte]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.4]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `blueprint_router` wird in `main.py` unter `/api` Prefix eingehangen.
- Service-Layer macht API-Tests unabhängig von HTTP-Details.
- Alle 9 Blueprint-API-Tests und 10 Service-Tests bestehen.

### File List

- `backend/api/blueprint_routes.py`
- `backend/services/blueprint_service.py`
- `backend/tests/test_blueprint_api.py`
- `backend/tests/test_blueprint_service.py`
- `frontend/app/utils/api-client.ts`
- `frontend/app/rat-architekt/page.tsx`
- `frontend/app/__tests__/api-client.test.ts`
