# Story 4.3: Konferenzzimmer — Live-Execution-UI

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **im Konferenzzimmer-Tab den laufenden Council in Echtzeit sehen**,
so dass ich **transparent nachvollziehen kann, was die KI gerade tut**.

## Acceptance Criteria

1. Eingabebereich für Prompt-Text und Mode-Toggle (Auto-Pilot / God Mode)
2. „Starten"-Button startet Blueprint-Run via `POST /api/councils/{id}/run`
3. WS-Verbindung öffnet sich → aktiver Node pulsiert gelb im Live-Canvas
4. Nach Abschluss: finales Dokument erscheint im Output-Bereich
5. Bei Fehler: klare Fehlermeldung mit Fehlergrund
6. God-Mode-Overlay erscheint bei `status=paused`

## Tasks / Subtasks

- [x] Task 1: `konferenzzimmer/page.tsx` Hauptkomponente (AC: 1–6)
  - [x] Subtask 1.1: Prompt-Eingabe + Blueprint-Auswahl-Dropdown
  - [x] Subtask 1.2: Mode-Toggle (Auto-Pilot / God Mode)
  - [x] Subtask 1.3: `useCouncilWebSocket` Hook-Integration
  - [x] Subtask 1.4: Live-Canvas (read-only React Flow)
  - [x] Subtask 1.5: Output-Bereich mit `whitespace-pre-wrap`
- [x] Task 2: God-Mode-Overlay-Komponente (AC: 6)
  - [x] Subtask 2.1: Approve / Reject / Modify Buttons
  - [x] Subtask 2.2: Modify-Modus: Textarea für Draft-Bearbeitung
- [x] Task 3: Blueprint-Run-Endpunkt `POST /api/councils/{id}/run` (AC: 2)
- [x] Task 4: `GET /api/councils/` für Blueprint-Liste im Dropdown

## Dev Notes

- Live-Canvas ist schreibgeschützt: `nodesDraggable={false}`, `nodesConnectable={false}`
- `markNodeActive(nodeName)` sucht Node per `data.label`-Übereinstimmung
- God-Mode-Overlay: `fixed inset-0` Backdrop mit zentriertem Modal

### Project Structure Notes

- `frontend/app/konferenzzimmer/page.tsx`
- Wiederverwendung: `ArchitectCanvas`, `useCouncilWebSocket`, `council-store`

### References

- [Source: _bmad-output/planning-artifacts/ux-design.md#User-Journey-God-Mode]
- [Source: _bmad-output/planning-artifacts/architecture.md#Sequenzdiagramm-Council-Run]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- Polling-Fallback für Blueprint-Liste: `councilApi.list()` beim Mount einmalig aufgerufen.
- God-Mode-Overlay nutzt `onPaused`-Callback aus `useCouncilWebSocket`.

### File List

- `frontend/app/konferenzzimmer/page.tsx`
