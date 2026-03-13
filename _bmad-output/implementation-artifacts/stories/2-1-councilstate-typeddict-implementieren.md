# Story 2.1: CouncilState TypedDict implementieren

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **den `CouncilState` TypedDict mit allen Feldern und Reducern**,
so dass er **das einzige State-Objekt für alle Agents ist**.

## Acceptance Criteria

1. `feedback_history: Annotated[List[str], operator.add]` — append-only Reducer
2. `messages: Annotated[list, operator.add]` — akkumulierend
3. `APPROVAL_THRESHOLD = 8.0` importierbar aus `state`
4. `MAX_ITERATIONS = 5` importierbar aus `state`
5. Alle Felder haben korrekte Typ-Annotationen (mypy-kompatibel)

## Tasks / Subtasks

- [x] Task 1: `state.py` mit `CouncilState` TypedDict (AC: 1–5)
  - [x] Subtask 1.1: `input_topic`, `current_draft`, `route_decision` (str)
  - [x] Subtask 1.2: `feedback_history` mit `operator.add` Reducer
  - [x] Subtask 1.3: `messages` mit `operator.add` Reducer
  - [x] Subtask 1.4: `iteration_count` (int), `critic_score` (Optional[float])
  - [x] Subtask 1.5: `run_id`, `active_node` (str)
- [x] Task 2: Konstanten `APPROVAL_THRESHOLD`, `MAX_ITERATIONS` (AC: 3, 4)
- [x] Task 3: Unit-Tests für Reducer-Verhalten (AC: 1, 2)
  - [x] Subtask 3.1: Test `feedback_history` akkumuliert
  - [x] Subtask 3.2: Test `messages` akkumuliert
  - [x] Subtask 3.3: Test Konstanten-Import

## Dev Notes

- `operator.add` als Reducer → Werte werden niemals überschrieben, nur angehängt
- `typing_extensions.TypedDict` für Python 3.10-Kompatibilität
- Bezug: `from typing import Annotated, List, Optional` und `import operator`

### Project Structure Notes

- `backend/state.py`
- `backend/tests/test_state.py`

### References

- [Source: CLAUDE.md#Architecture Concepts — CouncilState]
- [Source: _bmad-output/planning-artifacts/architecture.md#CouncilState-TypedDict]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `typing_extensions.TypedDict` statt `typing.TypedDict` für breitere Python-Kompatibilität.
- Tests benutzen `operator.add` direkt um Reducer-Semantik zu validieren.

### File List

- `backend/state.py`
- `backend/tests/test_state.py`
