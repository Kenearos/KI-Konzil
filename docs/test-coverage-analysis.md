# Test Coverage Analysis — CouncilOS

**Date:** 2026-02-20
**Repository status:** Pre-code / architecture stage
**Coverage today:** 0% (no application code exists)

This document analyses the planned architecture defined in `CLAUDE.md` and `README.md`, identifies every testable unit, and prioritises the areas that carry the most risk if left untested.

---

## 1. Current State

The repository contains only `README.md` and `CLAUDE.md`. No production code, test files, or tooling configuration exist yet. Every recommendation below is therefore forward-looking: it defines the test strategy that must accompany each development phase rather than patching gaps in existing coverage.

---

## 2. Risk-Prioritised Coverage Areas

### 2.1 `CouncilState` and State Management (CRITICAL)

**Why critical:** `CouncilState` is the single source of truth passed between every agent. A bug here corrupts the entire pipeline silently.

**What to test:**

| Scenario | Type |
|---|---|
| `feedback_history` uses `operator.add` and appends across loop iterations — never overwrites | Unit |
| `messages` reducer accumulates correctly when agents return partial state | Unit |
| `route_decision` is always one of the allowed string literals (`"rework"`, `"approve"`, custom values) | Unit |
| Passing a state missing required fields raises a clear error at graph entry, not mid-run | Unit |
| A full loop (master → critic → rework → master → critic → approve) preserves all prior feedback in history | Integration |

**File to test:** `backend/state.py`

---

### 2.2 Routing Logic (CRITICAL)

**Why critical:** The conditional edges are the core business logic. A routing bug sends documents into infinite loops or skips the critic entirely — the two worst failure modes for the product's value proposition.

**What to test:**

| Scenario | Type |
|---|---|
| Score < 8 → `route_decision = "rework"`, graph returns to master | Unit |
| Score ≥ 8 → `route_decision = "approve"`, graph advances to writer | Unit |
| Critic returns a non-numeric or malformed score — routing falls back safely (no crash) | Unit |
| Loop terminates after N iterations even if score never reaches threshold (guard against infinite loops) | Integration |
| Custom routing values defined in user blueprints are handled without exception | Unit |

**File to test:** `backend/agents/` (routing functions), `backend/services/graph_builder.py`

---

### 2.3 LangGraph Agent Node Functions (HIGH)

Each agent node function must be independently testable with mocked LLM responses.

**What to test per node:**

| Scenario | Type |
|---|---|
| Node receives a valid `CouncilState` and returns a dict with only the keys it owns | Unit |
| Node appends to `messages`, never replaces the full list | Unit |
| Node correctly uses its configured system prompt (verify prompt is sent as system message) | Unit |
| Node handles an empty `current_draft` gracefully (first iteration edge case) | Unit |
| Critic node produces a numeric score in the expected range within `route_decision` output | Unit |
| Master node incorporates all items in `feedback_history` into its revised draft prompt | Unit |

**Key rule from `CLAUDE.md`:** LLM calls must be mocked in CI — never make real API calls.

```python
# Example mock pattern for every agent node test
from unittest.mock import patch, MagicMock

@patch("backend.agents.master_agent.ChatAnthropic")
def test_master_agent_node_appends_to_messages(mock_llm):
    mock_llm.return_value.invoke.return_value = MagicMock(content="Draft v2")
    state = CouncilState(
        input_topic="Write a blog post",
        current_draft="Draft v1",
        feedback_history=["Too short"],
        route_decision="",
        messages=[],
    )
    result = master_agent_node(state)
    assert len(result["messages"]) == 1
    assert result["current_draft"] == "Draft v2"
```

---

### 2.4 Dynamic Graph Builder (HIGH)

**Why high:** From Phase 3 onward the graph is built at runtime from a user-supplied JSON blueprint. A parsing error or invalid edge definition produces a graph that silently misbehaves.

**What to test:**

| Scenario | Type |
|---|---|
| A valid blueprint JSON produces a compilable `StateGraph` | Unit |
| Blueprint with a conditional edge correctly wires the routing function | Unit |
| Blueprint with a cycle (A → B → A) compiles without flattening the cycle | Unit |
| Blueprint referencing a non-existent node ID raises a descriptive `ValueError`, not a Python `KeyError` | Unit |
| Blueprint with zero nodes raises a clear error | Unit |
| Blueprint with two nodes and no edges raises a clear error | Unit |
| A blueprint that was serialised from the frontend and round-tripped through PostgreSQL produces the same graph | Integration |

**File to test:** `backend/services/graph_builder.py`

---

### 2.5 Blueprint JSON Parser (HIGH — Frontend)

**Why high:** The parser converts a React Flow canvas into the JSON that controls backend execution. Any data loss or structural error here means user-designed councils don't run as intended.

**What to test:**

| Scenario | Type |
|---|---|
| A two-node linear graph emits correct `nodes` + `edges` JSON | Unit |
| A conditional edge with a `condition` label is preserved in output | Unit |
| An isolated node (no edges) is flagged as a warning, not silently dropped | Unit |
| Node with empty `systemPrompt` field is preserved (validation happens at run time, not parse time) | Unit |
| Blueprint JSON includes a `version` field | Unit |
| Re-parsing a previously saved blueprint produces identical output (idempotency) | Unit |

**File to test:** `frontend/src/utils/parser.ts` (or `.js`)

---

### 2.6 FastAPI REST Endpoints (MEDIUM-HIGH)

**What to test:**

| Endpoint | Scenario | Type |
|---|---|---|
| `POST /api/councils/` | Creates a blueprint, returns 201 with ID | Integration |
| `POST /api/councils/` | Payload missing required fields returns 422 | Integration |
| `GET /api/councils/{id}` | Returns stored blueprint | Integration |
| `GET /api/councils/{id}` | Non-existent ID returns 404 | Integration |
| `PUT /api/councils/{id}` | Updates blueprint, bumps `version` field | Integration |
| `DELETE /api/councils/{id}` | Removes blueprint, subsequent GET returns 404 | Integration |
| All endpoints | Unauthenticated requests (when auth is added) return 401 | Integration |

Use `httpx.AsyncClient` + `pytest-asyncio` for async FastAPI tests. Use a dedicated test database, never the production instance.

---

### 2.7 WebSocket Agent Status Events (MEDIUM-HIGH)

**Why this is risky:** WebSocket behaviour is easy to get right manually and easy to break silently. The frontend's live-highlighting feature depends entirely on these events arriving in the correct order.

**What to test:**

| Scenario | Type |
|---|---|
| Connecting to `/ws/council/{run_id}` returns a 101 upgrade | Integration |
| When LangGraph enters `master_agent_node`, the WebSocket emits `{"node": "master_agent", "status": "running"}` | Integration |
| When a node completes, a `"completed"` status event is emitted before the next node's `"running"` event | Integration |
| When the graph finishes, a `"done"` event is emitted with the final output | Integration |
| Client disconnect during a run does not crash the backend process | Integration |
| Two concurrent WebSocket sessions for different `run_id`s do not cross-contaminate events | Integration |

---

### 2.8 Human-in-the-Loop / God Mode (MEDIUM)

This is the most stateful and interactive code path and the hardest to test manually.

**What to test:**

| Scenario | Type |
|---|---|
| With `interrupt_before` configured, the graph pauses before the specified node | Integration |
| The paused state (including `current_draft` and `feedback_history`) is correctly surfaced to the frontend | Integration |
| Sending "approve" resumes execution and the graph continues from the paused node | Integration |
| Sending "reject" resumes execution with `route_decision = "rework"` | Integration |
| Modifying `current_draft` in the approval UI causes the next node to receive the modified content | Integration |
| Session timeout while paused: the run is marked as `timed_out`, not left in `paused` forever | Integration |

---

### 2.9 External Tool Wrappers (MEDIUM)

Tools must be tested in isolation with mocked external calls.

**Tavily Web Search:**

| Scenario | Type |
|---|---|
| Tool returns a list of results with `url` and `snippet` fields | Unit |
| Tavily API returns 429 (rate limit) — tool raises a retriable error | Unit |
| Tavily API is unreachable — tool raises a non-retriable error with a clear message | Unit |

**PyPDF + Vector Store:**

| Scenario | Type |
|---|---|
| A valid PDF is chunked and embedded without error | Unit |
| A password-protected PDF raises a clear error | Unit |
| A zero-byte file raises a clear error | Unit |
| Semantic search returns the top-K most relevant chunks | Unit |
| Vector store survives a restart and retrieves previously stored embeddings | Integration |

---

### 2.10 React Flow Custom Node Components (MEDIUM — Frontend)

**What to test:**

| Scenario | Type |
|---|---|
| Rendering a node with no props does not throw | Unit |
| Changing the `systemPrompt` field in the settings panel updates the node data | Unit |
| Selecting a different LLM model updates the node's model field | Unit |
| Toggling "Web Search" on/off reflects in node data | Unit |
| Node label truncates at a defined character limit without overflowing the card UI | Unit |

Use React Testing Library. Do not snapshot-test node styling — it changes too often and generates false negatives.

---

## 3. Test Infrastructure Recommendations

### Backend (`backend/`)

```
pytest
pytest-asyncio         # async FastAPI route tests
httpx                  # async test client for FastAPI
pytest-cov             # coverage reports
unittest.mock          # LLM mocking (stdlib, no extra dep)
factory-boy            # fixture factories for CouncilState
```

Minimum coverage target: **80% for `agents/`**, **90% for `state.py` and `services/graph_builder.py`**.

Configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.coverage.run]
omit = ["tests/*", "**/__init__.py"]

[tool.coverage.report]
fail_under = 80
```

### Frontend (`frontend/`)

```
vitest (or jest)
@testing-library/react
@testing-library/user-event
msw                    # Mock Service Worker for API/WebSocket mocking
```

---

## 4. What to Write First (Priority Order)

Build tests in this sequence — it matches the development phases and catches the highest-risk bugs earliest:

1. **`state.py` — `CouncilState` reducers** (write before any agent code)
2. **`agents/` — each node function** (write alongside each node implementation)
3. **Routing logic** (write before connecting the graph)
4. **`graph_builder.py`** (write alongside Phase 3 dynamic graph work)
5. **REST API endpoints** (write alongside Phase 2 blueprint persistence)
6. **Frontend parser** (write alongside Phase 2 React Flow work)
7. **WebSocket events** (write alongside Phase 3 integration work)
8. **God Mode / Human-in-the-Loop** (write alongside Phase 4)
9. **Tool wrappers** (write alongside Phase 4)

---

## 5. What to Avoid

- **Do not make real LLM API calls in any test.** This adds cost, latency, and flakiness. Always mock `ChatAnthropic` and `ChatOpenAI`.
- **Do not snapshot-test React Flow canvas state.** React Flow's internal node positions change non-deterministically and will make snapshot tests fail constantly.
- **Do not use a shared test database.** Each integration test that touches the database must run in a transaction that is rolled back after the test, or use a separate ephemeral schema.
- **Do not test the routing score threshold at exactly 8.** Always test both sides of the boundary (score = 7 → rework, score = 8 → approve, score = 9 → approve) to catch off-by-one errors in conditional logic.
- **Do not write end-to-end browser tests before Phase 3 is stable.** E2E tests on an unstable UI are expensive to maintain. Add Playwright/Cypress tests only once the API contract between frontend and backend is frozen.
