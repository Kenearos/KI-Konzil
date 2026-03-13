# Story 2.5: LangGraph-Graph bauen und ausführen

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **einen kompilierten LangGraph-Graphen** (`build_council_graph`),
so dass er **Master→Critic→(conditional)→Writer ausführt**.

## Acceptance Criteria

1. `build_council_graph()` gibt kompilierten, `invoke`-fähigen `StateGraph` zurück
2. Graph-Topologie: `master_agent → critic_agent → (rework: master_agent | approve: writer_agent) → END`
3. `route_after_critic(state)` liest `route_decision` und leitet korrekt weiter
4. `run_council_async()` führt den Graph in einem Thread-Pool aus (blockiert Event Loop nicht)
5. WebSocket-Callback `on_node_start` wird vor jedem Node aufgerufen

## Tasks / Subtasks

- [x] Task 1: `services/graph_builder.py` mit `build_council_graph()` (AC: 1, 2)
  - [x] Subtask 1.1: `StateGraph(CouncilState)` mit drei Nodes
  - [x] Subtask 1.2: `set_entry_point("master_agent")`
  - [x] Subtask 1.3: `add_conditional_edges` für Critic-Routing
- [x] Task 2: `route_after_critic(state)` Routing-Funktion (AC: 3)
- [x] Task 3: `run_council_async()` mit `asyncio.get_event_loop().run_in_executor()` (AC: 4, 5)
- [x] Task 4: Integration-Tests (LLMs gemockt) (AC: 1–3)

## Dev Notes

- `interrupt_before` nicht in Phase-1-Graph (nur in dynamischem Builder Phase 3)
- `on_node_start`-Callback: `lambda run_id, node_name: broadcast_event(run_id, {...})`
- Thread-Pool: `asyncio.get_event_loop().run_in_executor(None, graph.invoke, state)`

### Project Structure Notes

- `backend/services/graph_builder.py`
- `backend/tests/test_routing.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-002]
- [Source: CLAUDE.md#Key Design Constraints — Cycles are first-class]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `run_in_executor(None, ...)` nutzt Standard-Thread-Pool von asyncio; kein expliziter ThreadPoolExecutor nötig.
- Wrapper-Nodes für `on_node_start`-Callback werden zur Laufzeit um den Original-Node gelegt.

### File List

- `backend/services/graph_builder.py`
- `backend/tests/test_routing.py`
