# Story 2.2: Master-Agent-Node implementieren

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **den `master_agent_node`**,
so dass er **auf Basis von `input_topic` und `feedback_history` einen Draft erstellt**.

## Acceptance Criteria

1. Bei leerem `feedback_history` → Initialer Draft auf Basis von `input_topic`
2. Bei befülltem `feedback_history` → User-Prompt enthält Feedback-Einträge
3. Rückgabe enthält `current_draft` (nicht leer), `messages` (3 Elemente), `active_node = "master_agent"`
4. `iteration_count` wird um 1 erhöht
5. LLM: Claude 3.5 Sonnet, `temperature=0.7`

## Tasks / Subtasks

- [x] Task 1: `agents/master_agent.py` implementieren (AC: 1–5)
  - [x] Subtask 1.1: `_build_master_prompt(state)` für initiale vs. Feedback-Iterationen
  - [x] Subtask 1.2: `master_agent_node(state)` LangGraph-Node-Funktion
  - [x] Subtask 1.3: `SystemMessage`, `HumanMessage`, `AIMessage` in `messages`
- [x] Task 2: `agents/__init__.py` mit Exports
- [x] Task 3: Unit-Tests (AC: 1–4)
  - [x] Subtask 3.1: Test initiale Draft-Erstellung (kein Feedback)
  - [x] Subtask 3.2: Test Feedback-Integration im Prompt
  - [x] Subtask 3.3: Test `iteration_count` +1

## Dev Notes

- Mock-Pattern: `@patch("agents.master_agent.ChatAnthropic")`
- LLM-Aufruf: `llm.invoke([SystemMessage(...), HumanMessage(...)])` → AIMessage
- Bezug: `from langchain_anthropic import ChatAnthropic`, `from langchain_core.messages import ...`

### Project Structure Notes

- `backend/agents/master_agent.py`
- `backend/agents/__init__.py`
- `backend/tests/test_api.py` (integrationsähnliche Tests)

### References

- [Source: CLAUDE.md#Python Code Style]
- [Source: _bmad-output/planning-artifacts/architecture.md#CouncilState-TypedDict]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `_build_master_prompt()` unterscheidet via `if not state["feedback_history"]` zwischen erstem Aufruf und Iterations.
- `feedback_block` formatiert alle Feedback-Runden nummeriert.

### File List

- `backend/agents/master_agent.py`
- `backend/agents/__init__.py`
