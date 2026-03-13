# Story 3.1: React-Flow-Canvas mit Custom Agent Node

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **Agent-Nodes per Drag & Drop auf den Canvas ziehen**,
so dass ich **meinen KI-Rat visuell zusammenstellen kann**.

## Acceptance Criteria

1. Drag & Drop aus linker Seitenleiste → Custom `AgentNode` erscheint auf Canvas
2. Klick auf Node → rechtes `NodeSettingsPanel` öffnet sich
3. Änderung von Name/Prompt/Modell → Canvas-Node aktualisiert sich live (Zustand-Bindung)
4. Node zeigt: Name, LLM-Modell (farblich kodiert), Tool-Badges (🔍, 📄)
5. Pulsier-Animation (`animate-pulse`) wenn `isActive = true`

## Tasks / Subtasks

- [x] Task 1: `components/nodes/AgentNode.tsx` Custom React Flow Node (AC: 1, 4, 5)
  - [x] Subtask 1.1: Anzeige: Name, Modell-Badge, Tool-Icons (Globe, FileText)
  - [x] Subtask 1.2: `isActive`-Zustand → `animate-pulse` + Indigo-Rahmen
  - [x] Subtask 1.3: `Handle` (source + target) für Verbindungen
- [x] Task 2: `store/council-store.ts` Zustand-Store (AC: 3)
  - [x] Subtask 2.1: `nodes`, `edges`, `selectedNodeId`, `councilName`
  - [x] Subtask 2.2: `addAgentNode()`, `updateNodeData()`, `selectNode()`
- [x] Task 3: `components/panels/NodeSidebar.tsx` (AC: 1)
- [x] Task 4: `components/panels/NodeSettingsPanel.tsx` (AC: 2, 3)
- [x] Task 5: `components/ArchitectCanvas.tsx` React Flow Wrapper
- [x] Task 6: Frontend-Tests für Store und Parser (AC: 3)

## Dev Notes

- `NODE_TYPES = { agent: AgentNode }` in `ArchitectCanvas` registrieren
- Zustand via `useCouncilStore` (Zustand) — kein React-Kontext-Drill
- `memo()` für Performance bei vielen Nodes

### Project Structure Notes

- `frontend/app/components/nodes/AgentNode.tsx`
- `frontend/app/components/ArchitectCanvas.tsx`
- `frontend/app/components/panels/NodeSidebar.tsx`
- `frontend/app/components/panels/NodeSettingsPanel.tsx`
- `frontend/app/store/council-store.ts`
- `frontend/app/types/council.ts`

### References

- [Source: _bmad-output/planning-artifacts/ux-design.md#Agent-Node-Canvas-Element]
- [Source: CLAUDE.md#React-Conventions — custom node components]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `MODEL_LABELS` und `MODEL_COLORS` als Lookup-Maps für farbliche Modell-Kodierung.
- `memo()` verhindert unnötige Re-Renders bei vielen Nodes auf dem Canvas.

### File List

- `frontend/app/types/council.ts`
- `frontend/app/store/council-store.ts`
- `frontend/app/components/nodes/AgentNode.tsx`
- `frontend/app/components/ArchitectCanvas.tsx`
- `frontend/app/components/NavTabs.tsx`
- `frontend/app/components/panels/NodeSidebar.tsx`
- `frontend/app/components/panels/NodeSettingsPanel.tsx`
- `frontend/app/app/__tests__/council-store.test.ts`
