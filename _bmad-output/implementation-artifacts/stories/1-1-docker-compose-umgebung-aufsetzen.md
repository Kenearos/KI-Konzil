# Story 1.1: Docker-Compose-Umgebung aufsetzen

<!-- 🏃 Prepared by BMAD SM Skill — Agent: Bob (Scrum Master) -->
<!-- Skill Command: /bmad-agent-bmm-sm → [CS] Context Story -->

Status: done

## Story

Als **Entwickler**,
möchte ich **eine vollständige lokale Docker-Compose-Umgebung**,
so dass ich **ohne lokale Python/Node-Installation entwickeln kann**.

## Acceptance Criteria

1. `docker compose up -d` startet drei Services: `db` (PostgreSQL 16), `api` (FastAPI Port 8000), `frontend` (Next.js Port 3000)
2. `GET /api/health` gibt `{"status": "ok"}` zurück
3. Frontend ist unter `http://localhost:3000` erreichbar
4. `pg_isready` im db-Container antwortet mit `accepting connections`
5. Named Volumes: `postgres_data` und `chroma_data` sind definiert

## Tasks / Subtasks

- [x] Task 1: `docker-compose.yml` mit drei Services erstellen (AC: 1–4)
  - [x] Subtask 1.1: `db`-Service mit PostgreSQL 16-alpine, Healthcheck
  - [x] Subtask 1.2: `api`-Service mit `depends_on db`, `env_file: .env`, `chroma_data`-Volume
  - [x] Subtask 1.3: `frontend`-Service mit `NEXT_PUBLIC_API_URL`-Env
- [x] Task 2: `.env.example` mit allen Pflicht-Keys erstellen (AC: 5)
- [x] Task 3: `.gitignore` um `.env` erweitern
- [x] Task 4: `backend/Dockerfile` und `frontend/Dockerfile` erstellen

## Dev Notes

- `chroma_data` Volume wird auf `/app/chroma_db` im api-Container gemappt
- `postgres_data` Volume für DB-Persistenz über Neustarts hinweg
- `api` nutzt `service_healthy` Bedingung für db-Abhängigkeit

### Project Structure Notes

- `docker-compose.yml` im Projekt-Root
- `backend/Dockerfile` und `frontend/Dockerfile`

### References

- [Source: CLAUDE.md#Environment Variables]
- [Source: _bmad-output/planning-artifacts/architecture.md#Deployment-Architektur]

## Dev Agent Record

### Agent Model Used

Amelia (💻 BMAD Dev Agent)

### Completion Notes List

- PostgreSQL Healthcheck verhindert Race Condition beim API-Start.
- `chroma_data` Named Volume sichert ChromaDB-Persistenz zwischen Container-Neustarts.

### File List

- `docker-compose.yml`
- `.env.example`
- `backend/Dockerfile`
- `frontend/Dockerfile`
