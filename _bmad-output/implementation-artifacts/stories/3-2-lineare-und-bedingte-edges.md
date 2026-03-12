# Story 3.2: Lineare und bedingte Edges

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **Pfeile zwischen Nodes ziehen und als linear/bedingt markieren**,
so dass ich **den Workflow meines Councils definieren kann**.

## Acceptance Criteria

1. Verbindungsziehen zwischen Handles → lineare graue Edge entsteht
2. Klick auf Edge → `EdgeSettingsPanel` öffnet sich
3. Edge als „bedingt" markieren mit Condition-Label → gestrichelte rote Linie mit Label
4. Edge als „approve" markieren → grüne Linie mit Label
5. Edge-Typ und Condition werden im Zustand persistiert

## Tasks / Subtasks

- [x] Task 1: `components/edges/ConditionalEdge.tsx` Custom React Flow Edge (AC: 3, 4)
  - [x] Subtask 1.1: `SmoothStepPath` Basis-Routing
  - [x] Subtask 1.2: Farb-Kodierung: grau (linear), rot gestrichelt (rework), grün (approve)
  - [x] Subtask 1.3: Label-Rendering via `EdgeLabelRenderer`
- [x] Task 2: `components/panels/EdgeSettingsPanel.tsx` (AC: 2, 3, 4)
  - [x] Subtask 2.1: Typ-Auswahl (linear/conditional)
  - [x] Subtask 2.2: Condition-Label-Eingabe wenn `type = conditional`
- [x] Task 3: `store/council-store.ts` — `updateEdgeData()` Funktion (AC: 5)
- [x] Task 4: `EDGE_TYPES` Registrierung in `ArchitectCanvas`

## Dev Notes

- `EDGE_TYPES = { conditional: ConditionalEdge }` + `defaultEdgeType: "conditional"`
- Edge-Daten: `edge.data.type` (linear|conditional), `edge.data.condition` (string)
- `EdgeLabelRenderer` positioniert Label absolut relativ zum Edge-Mittelpunkt

### Project Structure Notes

- `frontend/app/components/edges/ConditionalEdge.tsx`
- `frontend/app/components/panels/EdgeSettingsPanel.tsx`

### References

- [Source: _bmad-output/planning-artifacts/ux-design.md#Edge-Verbindungspfeil]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `getSmoothStepPath` aus `@xyflow/react` liefert `edgePath`, `labelX`, `labelY` in einem Aufruf.
- Farben werden direkt via `stroke`-Prop auf `BaseEdge` gesetzt.

### File List

- `frontend/app/components/edges/ConditionalEdge.tsx`
- `frontend/app/components/panels/EdgeSettingsPanel.tsx`
