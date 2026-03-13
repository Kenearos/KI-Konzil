# Story 2.4: Writer-Agent-Node implementieren

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **den `writer_agent_node`**,
so dass er **den finalen, vom Critic genehmigten Draft professionell poliert**.

## Acceptance Criteria

1. Erhält `current_draft` aus State, gibt polierten finalen Draft zurück
2. `active_node = "writer_agent"` im Rückgabe-Dict
3. LLM: Claude 3.5 Sonnet, `temperature=0.3` (deterministische Ausgabe)
4. System-Prompt instruiert: Grammatik/Stil verbessern, Inhalt NICHT ändern
5. Tests: LLM gemockt, Rückgabe-Dict validiert

## Tasks / Subtasks

- [x] Task 1: `agents/writer_agent.py` implementieren (AC: 1–4)
  - [x] Subtask 1.1: `_SYSTEM_PROMPT` für finale Politur-Anweisung
  - [x] Subtask 1.2: `writer_agent_node(state)` LangGraph-Node-Funktion
  - [x] Subtask 1.3: Rückgabe: `current_draft`, `messages`, `active_node`
- [x] Task 2: Unit-Tests (AC: 1–3, 5)

## Dev Notes

- `temperature=0.3` für konsistente Formatierung (weniger Kreativität als Master)
- System-Prompt: "Do NOT change the factual content or overall structure"
- Einfachster der drei Agent-Nodes — kein bedingtes Routing

### Project Structure Notes

- `backend/agents/writer_agent.py`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.4]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- Writer-Agent gibt nur `current_draft`, `messages`, `active_node` zurück (kein `route_decision`).

### File List

- `backend/agents/writer_agent.py`
