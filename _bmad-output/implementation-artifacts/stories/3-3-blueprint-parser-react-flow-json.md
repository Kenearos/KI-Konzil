# Story 3.3: Blueprint-Parser (React Flow → JSON)

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **System**,
möchte ich **eine `parseGraphToBlueprint()`-Funktion**,
so dass sie **den Canvas-State in ein valides Blueprint-JSON konvertiert**.

## Acceptance Criteria

1. Nodes + Edges → `CouncilBlueprint` mit `version`, `name`, `nodes[]`, `edges[]`
2. Bedingte Edge → `type: "conditional"` und `condition: "<label>"` im Edge-JSON
3. Lineare Edge → `type: "linear"` ohne `condition`-Feld
4. `version: 1` als Startwert
5. Tests: Alle drei Fälle (linear, conditional, gemischt)

## Tasks / Subtasks

- [x] Task 1: `utils/blueprint-parser.ts` implementieren (AC: 1–4)
  - [x] Subtask 1.1: Nodes-Mapping: `id`, `label`, `systemPrompt`, `model`, `tools`, `position`
  - [x] Subtask 1.2: Edges-Mapping: `id`, `source`, `target`, `type`, optional `condition`
  - [x] Subtask 1.3: Rückgabe: `CouncilBlueprint` mit `version: 1`
- [x] Task 2: `types/council.ts` — `CouncilBlueprint`, `BlueprintNode`, `BlueprintEdge` (AC: 1)
- [x] Task 3: Vitest-Tests (AC: 1–5)
  - [x] Subtask 3.1: Test lineares Blueprint
  - [x] Subtask 3.2: Test bedingte Edge
  - [x] Subtask 3.3: Test leeres Canvas (0 Nodes/Edges)

## Dev Notes

- `existingId?: string` Parameter für Updates (PUT vs POST)
- Tool-Mapping: `webSearch`, `pdfReader` (camelCase im Frontend, snake_case im Backend)
- `EdgeType = "linear" | "conditional"` als Union-Typ

### Project Structure Notes

- `frontend/app/utils/blueprint-parser.ts`
- `frontend/app/types/council.ts`
- `frontend/app/__tests__/blueprint-parser.test.ts`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Blueprint-JSON-Schema]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `position`-Feld wird mitgespeichert, damit Blueprint-Reload die Node-Positionen wiederherstellt.
- `existingId` ermöglicht `PUT`-Updates ohne neue ID-Generierung.

### File List

- `frontend/app/utils/blueprint-parser.ts`
- `frontend/app/types/council.ts`
- `frontend/app/__tests__/blueprint-parser.test.ts`
- `frontend/app/__tests__/types.test.ts`
