# Story 4.1: Dynamischer Graph-Builder aus Blueprint-JSON

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->
<!-- Workflow: _bmad/bmm/workflows/4-implementation/create-story/workflow.yaml -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **`dynamic_graph_builder.py`**,
so dass er **aus einem Blueprint-JSON zur Laufzeit einen kompilierten LangGraph-Graphen baut, der Zyklen korrekt erhält**.

## Acceptance Criteria

1. Valides Blueprint-JSON mit N Nodes → kompilierter `StateGraph`
2. Blueprint mit Zyklus (A→B→A, bedingt) → Graph kompiliert, Zyklus erhalten
3. Blueprint mit nicht-existenter Node-ID in Edge → `ValueError` mit sprechender Fehlermeldung
4. Blueprint mit 0 Nodes → `ValueError`
5. Blueprint mit 2 Nodes, 0 Edges → `ValueError`
6. Bedingte Edge mit `condition`-Label wird korrekt als conditional edge verdrahtet
7. Nodes mit `tools.web_search = true` bekommen Tavily-Tool gebunden
8. Nodes mit `tools.pdf_reader = true` bekommen PDF-Search-Tool gebunden

## Tasks / Subtasks

- [x] Task 1: Blueprint-JSON-Schema validieren (AC: 3, 4, 5)
  - [x] Subtask 1.1: Prüfen ob `nodes` nicht leer
  - [x] Subtask 1.2: Alle Edge `source`/`target` IDs auf Existenz in `nodes` prüfen
  - [x] Subtask 1.3: Sicherstellen ≥1 Edge vorhanden
- [x] Task 2: Node-Funktionen dynamisch erzeugen (AC: 1, 7, 8)
  - [x] Subtask 2.1: Agent-Node-Fabrik mit konfigurierbarem System-Prompt und Modell
  - [x] Subtask 2.2: Tool-Binding für web_search/pdf_reader
- [x] Task 3: Graph-Topologie aufbauen (AC: 1, 2, 6)
  - [x] Subtask 3.1: Entry-Point = erster Node ohne eingehende Edges
  - [x] Subtask 3.2: Lineare Edges als `add_edge`
  - [x] Subtask 3.3: Bedingte Edges als `add_conditional_edges` mit Routing-Funktion
- [x] Task 4: God-Mode-Unterstützung via `interrupt_before` (AC für Story 5.3)
  - [x] Subtask 4.1: `interrupt_before=node_ids` beim Kompilieren setzen
- [x] Task 5: Unit-Tests (AC: 1–6)
  - [x] Subtask 5.1: Test valides Blueprint
  - [x] Subtask 5.2: Test Blueprint mit Zyklus
  - [x] Subtask 5.3: Test Blueprint mit ungültiger Edge (ValueError)
  - [x] Subtask 5.4: Test Blueprint mit 0 Nodes (ValueError)

## Dev Notes

- **Zyklen sind First-Class**: Niemals den Graphen zu einem DAG vereinfachen.
- **Entry-Point-Erkennung**: Node ohne eingehende Edges = Startpunkt. Bei Zyklen: erster Node in `nodes`-Array.
- **Routing-Funktion**: Dynamisch erzeugte Closure über `route_decision`-State-Feld.
- Bezug: `backend/state.py`, `backend/services/graph_builder.py` (Phase-1-Referenz)

### Project Structure Notes

- Implementiert in: `backend/services/dynamic_graph_builder.py`
- Tests in: `backend/tests/test_dynamic_graph_builder.py`
- Nutzt: `backend/tools/web_search.py`, `backend/tools/pdf_reader.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-004] — Dynamischer Graph-Builder
- [Source: _bmad-output/planning-artifacts/architecture.md#Blueprint-JSON-Schema] — Datenformat
- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.1] — ACs
- [Source: CLAUDE.md#Key Design Constraints] — Zyklen sind First-Class

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent) — `dev-story` workflow

### Completion Notes List

- Entry-Point-Erkennung via Set-Differenz: `{alle Node-IDs} - {IDs die als Edge-Target vorkommen}`
- Routing-Closure für bedingte Edges: `lambda state: state.get("route_decision", "rework")`
- `interrupt_before` wird als Liste aller Node-IDs gesetzt wenn `god_mode=True`

### File List

- `backend/services/dynamic_graph_builder.py`
- `backend/tests/test_dynamic_graph_builder.py`
