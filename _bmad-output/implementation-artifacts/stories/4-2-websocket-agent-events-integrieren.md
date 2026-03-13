# Story 4.2: WebSocket-Agent-Events integrieren

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Frontend**,
möchte ich **WebSocket-Events vom Backend**,
so dass **der aktive Node im Canvas in Echtzeit pulsiert**.

## Acceptance Criteria

1. Backend sendet `{"event": "node_active", "node": "master_agent", ...}` bei Node-Eintritt
2. Backend sendet `{"event": "run_complete", "final_draft": "..."}` nach Abschluss
3. Backend sendet `{"event": "run_paused", "next_nodes": [...]}` bei God-Mode-Pause
4. Frontend `useCouncilWebSocket` Hook verbindet sich mit `WS /ws/council/{run_id}`
5. `markNodeActive(nodeName)` setzt `isActive = true` für den entsprechenden Canvas-Node
6. Bei WS-Verbindungsabbruch: Graceful-Handling ohne Crash

## Tasks / Subtasks

- [x] Task 1: `api/websocket.py` WebSocket-Endpoint (AC: 1–3)
  - [x] Subtask 1.1: `_connections` Dict für aktive WS-Sessions
  - [x] Subtask 1.2: `broadcast_event(run_id, event)` Funktion
  - [x] Subtask 1.3: `WS /ws/council/{run_id}` Route
- [x] Task 2: `hooks/useCouncilWebSocket.ts` (AC: 4–6)
  - [x] Subtask 2.1: `onComplete`, `onError`, `onPaused`, `onResumed` Callbacks
  - [x] Subtask 2.2: Event-Dispatching per `event.type`
  - [x] Subtask 2.3: Cleanup bei Unmount / Verbindungsabbruch
- [x] Task 3: Store-Integration: `markNodeActive(nodeName)` (AC: 5)
- [x] Task 4: WS-Router in `main.py` registrieren (AC: 1)

## Dev Notes

- `broadcast_event()` bereinigt tote Verbindungen automatisch (disconnected-Liste)
- Frontend: `useRef(null)` für WS-Instanz → sicheres Cleanup in useEffect-Return
- Event-Typen: `node_active`, `run_complete`, `run_paused`, `run_failed`

### Project Structure Notes

- `backend/api/websocket.py`
- `frontend/app/hooks/useCouncilWebSocket.ts`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-003]
- [Source: _bmad-output/planning-artifacts/architecture.md#WebSocket]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- WebSocket-Verbindungen werden per `run_id` isoliert — kein Cross-Event zwischen Runs.
- `try/except` in `broadcast_event()` verhindert, dass ein einzelner WS-Fehler alle Clients betrifft.

### File List

- `backend/api/websocket.py`
- `frontend/app/hooks/useCouncilWebSocket.ts`
