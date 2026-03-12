# Story 5.1: Tavily Web-Suche als Agent-Tool

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **Web-Suche als optionales Tool für jeden Agent**,
so dass **Agents aktuelle Informationen aus dem Internet nutzen können**.

## Acceptance Criteria

1. Agent mit `tools.web_search = true` → `web_search`-Tool wird gebunden
2. `TAVILY_API_KEY` gesetzt → formatierte Trefferliste wird zurückgegeben
3. `TAVILY_API_KEY` nicht gesetzt → Fehlermeldung, kein Crash
4. `max_results=5` als Standard; `search_depth="basic"`
5. Tests: gemockt via `@patch("tools.web_search.TavilyClient")`

## Tasks / Subtasks

- [x] Task 1: `tools/web_search.py` mit `@tool`-Decorator (AC: 1–4)
  - [x] Subtask 1.1: `TavilyClient`-Import (lazy, innerhalb der Funktion)
  - [x] Subtask 1.2: API-Key-Check vor Client-Initialisierung (AC: 3)
  - [x] Subtask 1.3: Response-Formatierung: Titel, URL, Snippet
- [x] Task 2: Tool-Binding im dynamischen Graph-Builder (AC: 1)
  - [x] Subtask 2.1: `tools.web_search = true` → `llm.bind_tools([web_search])`
- [x] Task 3: Unit-Tests (AC: 2, 3, 5)

## Dev Notes

- `from tavily import TavilyClient` lazy import — kein `ImportError` wenn nicht installiert
- LangChain `@tool`-Decorator macht die Funktion Tool-Aufruf-kompatibel
- Fehlerpfad gibt `"[Web Search Error] ..."` String zurück (kein Exception-Raise)

### Project Structure Notes

- `backend/tools/web_search.py`
- `backend/tests/test_tools.py`

### References

- [Source: _bmad-output/planning-artifacts/prd.md#FR-05.2]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- Lazy-Import von `TavilyClient` verhindert `ImportError` in Umgebungen ohne das Paket.
- Mock-Pattern: `@patch("tools.web_search.TavilyClient")` mockt direkt den Client.

### File List

- `backend/tools/web_search.py`
- `backend/tools/__init__.py`
- `backend/tests/test_tools.py`
