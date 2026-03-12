# Story 2.3: Critic-Agent-Node implementieren

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->
<!-- Workflow: _bmad/bmm/workflows/4-implementation/create-story/workflow.yaml -->

Status: done

## Story

Als **Backend-Entwickler**,
möchte ich **den `critic_agent_node` mit Score-Parsing, Routing-Logik und Safety-Valve**,
so dass er **Drafts bewertet, `route_decision` korrekt setzt und Endlosschleifen verhindert**.

## Acceptance Criteria

1. Score < 8 → `route_decision = "rework"`, Feedback wird an `feedback_history` angehängt
2. Score ≥ 8 → `route_decision = "approve"`, `feedback_history` bleibt unverändert
3. `iteration_count >= MAX_ITERATIONS` → automatische Genehmigung ohne LLM-Aufruf (Safety Valve)
4. Nicht-parsbare LLM-Antwort → Fallback `route_decision = "rework"`, kein Crash
5. Score wird auf 0–10 geclampt (kein Overflow)

## Tasks / Subtasks

- [x] Task 1: `_parse_critic_response()` implementieren (AC: 1, 4, 5)
  - [x] Subtask 1.1: Regex für SCORE, VERDICT, FEEDBACK-Blöcke
  - [x] Subtask 1.2: Score-Clamping (max 0.0, min 10.0)
  - [x] Subtask 1.3: Fallback auf (0.0, "rework", full_content) bei Parse-Fehler
- [x] Task 2: `critic_agent_node()` implementieren (AC: 1, 2, 3)
  - [x] Subtask 2.1: Safety-Valve prüfen vor LLM-Aufruf
  - [x] Subtask 2.2: LLM-Aufruf mit temperature=0.2
  - [x] Subtask 2.3: Route-Decision aus Score und APPROVAL_THRESHOLD ableiten
  - [x] Subtask 2.4: `feedback_history` nur bei rework anhängen
- [x] Task 3: Unit-Tests schreiben (AC: 1–5)
  - [x] Subtask 3.1: Test score < 8 → rework
  - [x] Subtask 3.2: Test score ≥ 8 → approve
  - [x] Subtask 3.3: Test safety valve bei MAX_ITERATIONS
  - [x] Subtask 3.4: Test Parse-Fehler-Fallback

## Dev Notes

- **LLM-Mocking:** `@patch("agents.critic_agent.ChatAnthropic")` in allen Unit-Tests
- **Kein echter API-Aufruf in CI** — strikte Anforderung aus CLAUDE.md
- **Threshold-Tests:** Immer beide Seiten testen (score=7.9 → rework, score=8.0 → approve)
- Bezug: `backend/state.py#APPROVAL_THRESHOLD`, `backend/state.py#MAX_ITERATIONS`

### Project Structure Notes

- Implementiert in: `backend/agents/critic_agent.py`
- Tests in: `backend/tests/test_routing.py`

### References

- [Source: CLAUDE.md#Python Code Style] — Type hints mandatory
- [Source: _bmad-output/planning-artifacts/architecture.md#CouncilState] — State contract
- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.3] — ACs

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent) — `dev-story` workflow

### Completion Notes List

- Score-Clamping verhindert Werte außerhalb 0–10 auch bei fehlerhafter LLM-Formatierung.
- Safety-Valve gibt `APPROVAL_THRESHOLD` als Score zurück (nicht 10.0), damit Tests einheitlich bleiben.
- Feedback wird nur bei `rework` angehängt, da `operator.add`-Reducer andernfalls Genehmigungen in die History schreibt.

### File List

- `backend/agents/critic_agent.py`
- `backend/tests/test_routing.py`
- `backend/state.py` (nur gelesen, nicht verändert)
