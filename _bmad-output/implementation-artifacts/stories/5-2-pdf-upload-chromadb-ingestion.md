# Story 5.2: PDF-Upload & ChromaDB-Ingestion

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Nutzer**,
möchte ich **ein PDF hochladen, das als Wissensquelle für Agents dient**,
so dass **Agents auf Inhalte aus langen Dokumenten zugreifen können**.

## Acceptance Criteria

1. `POST /api/councils/upload-pdf` mit PDF → `chunks_ingested` in Response
2. Nicht-PDF-Datei → `400 Bad Request`
3. PDF wird in Chunks aufgeteilt (PyPDF + LangChain TextSplitter) und in ChromaDB gespeichert
4. `pdf_search(query)` gibt Top-K semantisch ähnliche Chunks zurück
5. Agent mit `tools.pdf_reader = true` bekommt `pdf_search`-Tool gebunden

## Tasks / Subtasks

- [x] Task 1: `tools/pdf_reader.py` (AC: 3, 4)
  - [x] Subtask 1.1: `ingest_pdf(file_path)` → Chunks → ChromaDB
  - [x] Subtask 1.2: `pdf_search(query, top_k)` → semantische Suche
  - [x] Subtask 1.3: `_get_chroma_collection()` mit In-Memory-Cache
- [x] Task 2: `POST /api/councils/upload-pdf` Endpunkt in `routes.py` (AC: 1, 2)
  - [x] Subtask 2.1: `UploadFile` + MIME-Type-Validierung
  - [x] Subtask 2.2: Temp-Datei erstellen, `ingest_pdf()` aufrufen, bereinigen
- [x] Task 3: Tool-Binding im dynamischen Graph-Builder (AC: 5)
- [x] Task 4: Unit-Tests (gemockt) (AC: 1–4)

## Dev Notes

- ChromaDB `PersistentClient` mit `CHROMA_PERSIST_DIR`-Umgebungsvariable
- Cosine-Similarity als Distance-Metrik: `{"hnsw:space": "cosine"}`
- `_collection_cache` dict verhindert mehrfache ChromaDB-Initialisierungen
- Tests mocken `chromadb.PersistentClient` komplett

### Project Structure Notes

- `backend/tools/pdf_reader.py`
- `backend/tests/test_tools.py`

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#ADR-006]
- [Source: _bmad-output/planning-artifacts/prd.md#FR-05.3]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- `UploadFile.content_type` für MIME-Validierung; `.filename.endswith(".pdf")` als Fallback.
- `tempfile.NamedTemporaryFile` mit `delete=False` für sicheres Temp-File-Handling.
- ChromaDB-Kollektion wird pro `collection_name` gecacht.

### File List

- `backend/tools/pdf_reader.py`
- `backend/tests/test_tools.py`
