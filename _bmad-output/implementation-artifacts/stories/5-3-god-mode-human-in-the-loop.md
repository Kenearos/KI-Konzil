# Story 5.3: God Mode — Human-in-the-Loop

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->
<!-- Workflow: _bmad/bmm/workflows/4-implementation/create-story/workflow.yaml -->

Status: done

## Story

Als **Nutzer**,
möchte ich **im God Mode jeden Schritt des Councils genehmigen, ablehnen oder modifizieren**,
so dass ich **volle Kontrolle über den KI-Prozess habe und kritische Entscheidungen absegnen kann**.

## Acceptance Criteria

1. `god_mode=true` → Graph pausiert via `interrupt_before` nach dem ersten Node-Abschluss
2. `POST /approve` mit `action=approve` → Run setzt am nächsten Node fort
3. `POST /approve` mit `action=reject` → Run bricht mit `status=failed` ab
4. `POST /approve` mit `action=modify` und `modified_state` → Run setzt mit modifiziertem Draft fort
5. `GET /councils/run/{run_id}/state` gibt den pausierten State zurück (inkl. `current_draft`, `next_nodes`)
6. Frontend-Overlay erscheint bei `status=paused` und zeigt Agent-Name, aktuellen Draft und drei Buttons
7. Zwei parallele god-mode Runs kontaminieren sich nicht gegenseitig (Session-Isolation)
8. Zweimaliges Approve ohne laufenden Run gibt `400 Bad Request` zurück

## Tasks / Subtasks

- [x] Task 1: `interrupt_before` in dynamischem Graph-Builder implementieren (AC: 1)
  - [x] Subtask 1.1: `compile(interrupt_before=[...alle node IDs...])` bei `god_mode=True`
  - [x] Subtask 1.2: Nach `graph.invoke()` auf `__interrupt__`-Signal prüfen
- [x] Task 2: God-Mode-State-Verwaltung implementieren (AC: 1, 5, 7)
  - [x] Subtask 2.1: `_god_mode_sessions: dict[run_id, GodModeSession]` in-memory
  - [x] Subtask 2.2: `GodModeSession` mit `graph`, `config`, `current_state`, `next_nodes`
  - [x] Subtask 2.3: Session-Isolation sicherstellen (kein shared-state)
- [x] Task 3: Resume-Logik implementieren (AC: 2, 3, 4)
  - [x] Subtask 3.1: `resume_god_mode(run_id, action, modified_state)` Funktion
  - [x] Subtask 3.2: Bei `modify`: State-Override vor `graph.invoke(None, config)`
  - [x] Subtask 3.3: Bei `reject`: Session löschen, Status auf `failed`
- [x] Task 4: API-Endpunkte (AC: 2–5, 8)
  - [x] Subtask 4.1: `POST /councils/run/{run_id}/approve` Route
  - [x] Subtask 4.2: `GET /councils/run/{run_id}/state` Route
  - [x] Subtask 4.3: `400`-Guard wenn Session nicht pausiert
- [x] Task 5: Frontend God-Mode-UI (AC: 6)
  - [x] Subtask 5.1: Polling `GET /councils/run/{run_id}` auf `status=paused`
  - [x] Subtask 5.2: Overlay-Komponente mit Draft-Text, Agent-Name, drei Buttons
  - [x] Subtask 5.3: Modify-Modus mit Textarea für Draft-Bearbeitung
- [x] Task 6: Tests (AC: 1–5, 7, 8)
  - [x] Subtask 6.1: `test_god_mode.py` — alle AC als Tests

## Dev Notes

- **LangGraph `interrupt_before`**: Dies ist der einzige Pause-Mechanismus — kein eigener einbauen.
- **`graph.invoke(None, config)`**: Der `None`-Input setzt die Ausführung nach einem Interrupt fort.
- **God-Mode-State-Isolation**: Jede `run_id` hat eine eigene Session-Instanz im Dict.
- **Thread Safety**: Da LangGraph-Invokes in `run_in_executor` laufen, muss der Session-Store thread-safe sein.
- Bezug: `backend/services/dynamic_graph_builder.py`, LangGraph-Dokumentation zu `interrupt_before`

### Project Structure Notes

- Implementiert in: `backend/services/dynamic_graph_builder.py` (GodMode-Logik)
- Implementiert in: `backend/api/routes.py` (Endpunkte)
- Frontend: `frontend/app/konferenzzimmer/page.tsx` (Overlay)
- Tests in: `backend/tests/test_god_mode.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-001] — LangGraph interrupt_before
- [Source: _bmad-output/planning-artifacts/architecture.md#God-Mode-Sequenzdiagramm]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.3] — ACs
- [Source: CLAUDE.md#Key Design Constraints] — Human-in-the-Loop via interrupt_before

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent) — `dev-story` workflow

### Completion Notes List

- LangGraph `interrupt_before` gibt nach Pause eine `Command`-Instanz zurück; der Typ wird via `isinstance` geprüft.
- Der `config`-Parameter (`{"configurable": {"thread_id": run_id}}`) wird für LangGraph-Checkpointer benötigt.
- In-Memory-Sessions gehen bei Server-Neustart verloren — für MVP akzeptabel.

### File List

- `backend/services/dynamic_graph_builder.py`
- `backend/api/routes.py`
- `backend/tests/test_god_mode.py`
- `frontend/app/konferenzzimmer/page.tsx`
