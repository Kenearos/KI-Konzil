---
stepsCompleted:
  - step-v-01-discovery
  - step-v-02-structure
  - step-v-03-goals
  - step-v-04-requirements
  - step-v-05-measurability-validation
  - step-v-06-traceability-validation
  - step-v-10-smart-validation
  - step-v-11-holistic-quality-validation
  - step-v-12-completeness-validation
inputDocuments:
  - README.md
  - CLAUDE.md
workflowType: 'prd'
---

# Product Requirements Document — CouncilOS (KI-Rat Baukasten)

**Autor:** KI-Konzil Dev-Team
**Datum:** 2026-03-12
**Version:** 1.0.0
**Status:** Genehmigt

---

## 1. Projekt-Überblick

### 1.1 Problemstellung

Aktuelle KI-Tools (wie ChatGPT) arbeiten linear. Wenn ein Nutzer ein komplexes Ergebnis will — z. B. einen perfekten Blogartikel, rechtssichere PR-Texte oder lauffähigen Code — muss er den Output ständig manuell lesen, Fehler finden und die KI in endlosen Chat-Verläufen korrigieren. Das kostet Zeit und erfordert extrem gutes „Prompting".

### 1.2 Lösung

**CouncilOS** ist eine visuelle No-Code-Plattform. Anstatt selbst mit der KI zu chatten, baut der Nutzer sich einen eigenen **„KI-Rat" (Multi-Agenten-System)**. Der Nutzer definiert verschiedene KI-Experten, gibt ihnen Werkzeuge (Internet, PDF-Reader) und legt per Drag & Drop fest, in welcher Reihenfolge sie Dokumente bearbeiten, kritisieren und überarbeiten.

### 1.3 Alleinstellungsmerkmal (USP)

Im Gegensatz zu bestehenden Tools arbeiten die KIs in **Endlosschleifen (Zyklen)**. Eine Kritiker-KI kann ein Dokument so lange an die Master-KI zurückweisen, bis es perfekt ist, ohne dass der Mensch eingreifen muss. Wahlweise kann der Mensch als „Vorsitzender des Rates" jeden Schritt abnicken (God-Mode / Human-in-the-Loop).

---

## 2. Ziele und Erfolgsmetriken

### 2.1 Geschäftsziele

| Ziel | Messgröße | Zielwert |
|------|-----------|---------- |
| Nutzer können komplexe KI-Pipelines ohne Code aufbauen | Anzahl erfolgreich abgeschlossener Council-Runs | ≥ 100 Runs/Woche (Phase 3 Launch) |
| Qualitätsverbesserung durch iterative Schleifen | Durchschnittlicher Critic-Score bei Abschluss | ≥ 8/10 |
| Transparente KI-Nutzung | Anteil der Nutzer, die God-Mode verwenden | ≥ 20 % aller Runs |

### 2.2 Nutzerziele

- Nutzer können in < 5 Minuten einen KI-Rat aus Standard-Agents zusammenstellen und ausführen.
- Nutzer sehen in Echtzeit, welcher Agent gerade arbeitet.
- Im God Mode können Nutzer an jedem Entscheidungspunkt eingreifen.

### 2.3 Technische Ziele

- Backend-Latenz für einen einzelnen Agent-Node < 30 Sekunden (bei normalen LLM-Antwortzeiten).
- WebSocket-Events werden innerhalb von 500 ms nach Node-Eintritt gesendet.
- Das System unterstützt bis zu 10 gleichzeitige Council-Runs.

---

## 3. Zielgruppen

### 3.1 Primäre Nutzer

**Content-Ersteller und Marketing-Teams**
- Erstellen Rohtexte, die von KI-Experten (SEO, Faktenprüfung, Lektor) in Schleifen verfeinert werden.
- Technisches Know-how: gering bis mittel.
- Kernbedürfnis: Qualitätssteigerung ohne manuelles Nacharbeiten.

**Software-Entwickler und Architekten**
- Lassen Code durch Architekten-KI, Tester-KI und Doku-KI überprüfen.
- Technisches Know-how: hoch.
- Kernbedürfnis: Automatisierte Code-Review-Schleifen.

### 3.2 Sekundäre Nutzer

**Analysten und Researcher**
- Lassen 100-seitige PDFs durch KI-Ketten zusammenfassen und analysieren.
- Kernbedürfnis: Informationsextraktion aus langen Dokumenten.

---

## 4. Funktionale Anforderungen

### FR-01: Visueller Canvas (Rat-Architekt)

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| FR-01.1 | Der Nutzer kann Agent-Nodes per Drag & Drop auf den Canvas ziehen. | MUSS |
| FR-01.2 | Ein Klick auf einen Node öffnet ein Einstellungs-Panel (Name, System-Prompt, LLM-Modell, Tools). | MUSS |
| FR-01.3 | Der Nutzer kann lineare Edges (Pfeile) zwischen Nodes ziehen. | MUSS |
| FR-01.4 | Der Nutzer kann bedingte Edges erstellen (mit Routing-Label). | MUSS |
| FR-01.5 | Der Nutzer kann den Council unter einem Namen speichern. | MUSS |
| FR-01.6 | Der Nutzer kann einen gespeicherten Council laden und bearbeiten. | SOLL |
| FR-01.7 | Der Canvas unterstützt Export des Blueprints als JSON-Datei. | SOLL |

### FR-02: Council-Ausführung (Konferenzzimmer)

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| FR-02.1 | Der Nutzer kann einen Prompt-Text als Eingabe für den Council angeben. | MUSS |
| FR-02.2 | Der Nutzer kann ein PDF hochladen, dessen Inhalt als Eingabe dient. | SOLL |
| FR-02.3 | Der Nutzer kann zwischen Auto-Pilot und God Mode wählen. | MUSS |
| FR-02.4 | Im Auto-Pilot läuft der Council autonom bis zum Abschluss. | MUSS |
| FR-02.5 | Im God Mode pausiert der Council vor jedem Agent und wartet auf Genehmigung. | MUSS |
| FR-02.6 | Der Nutzer sieht das fertige Dokument nach Abschluss des Councils. | MUSS |
| FR-02.7 | Der Nutzer kann vergangene Council-Runs in einem Verlauf einsehen. | SOLL |

### FR-03: Echtzeit-Updates (WebSocket)

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| FR-03.1 | Der aktive Agent-Node leuchtet/pulsiert im Canvas (live). | MUSS |
| FR-03.2 | WebSocket-Events enthalten: `node_name`, `status` (`running`/`completed`/`done`). | MUSS |
| FR-03.3 | Bei Abschluss eines Runs wird ein `done`-Event gesendet. | MUSS |

### FR-04: God Mode / Human-in-the-Loop

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| FR-04.1 | Im God Mode erscheint ein Popup mit dem Agent-Namen, Grund und Approve/Reject/Modify-Buttons. | MUSS |
| FR-04.2 | „Approve" setzt die Ausführung am nächsten Node fort. | MUSS |
| FR-04.3 | „Reject" bricht den Run ab und markiert ihn als fehlgeschlagen. | MUSS |
| FR-04.4 | „Modify" erlaubt die Bearbeitung des aktuellen Drafts vor Fortsetzung. | SOLL |

### FR-05: Agent-Konfiguration

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| FR-05.1 | Jeder Agent kann ein individuelles LLM-Modell zugewiesen bekommen (Claude 3.5 Sonnet, GPT-4o, lokal). | MUSS |
| FR-05.2 | Jeder Agent kann optional Web-Suche aktiviert bekommen (Tavily). | SOLL |
| FR-05.3 | Jeder Agent kann optional PDF-Reader aktiviert bekommen (ChromaDB). | SOLL |
| FR-05.4 | Agent-Konfigurationen können gespeichert und wiederverwendet werden. | SOLL |

### FR-06: Blueprint-Verwaltung (CRUD)

| ID | Anforderung | Priorität |
|----|-------------|-----------|
| FR-06.1 | Blueprints können erstellt, gelesen, aktualisiert und gelöscht werden (REST API). | MUSS |
| FR-06.2 | Blueprints werden in PostgreSQL als JSONB gespeichert. | MUSS |
| FR-06.3 | Jeder Blueprint hat ein `version`-Feld. | MUSS |

---

## 5. Nicht-funktionale Anforderungen

### NFR-01: Performance

| ID | Anforderung |
|----|-------------|
| NFR-01.1 | WebSocket-Events werden innerhalb von 500 ms nach Node-Eintritt gesendet. |
| NFR-01.2 | Blueprint-CRUD-Endpunkte antworten in < 200 ms (P95). |
| NFR-01.3 | Das System unterstützt ≥ 10 parallele Council-Runs. |

### NFR-02: Sicherheit

| ID | Anforderung |
|----|-------------|
| NFR-02.1 | API-Keys (Anthropic, OpenAI, Tavily) werden ausschließlich in Umgebungsvariablen gespeichert, nie im Code. |
| NFR-02.2 | Keine echten LLM-API-Aufrufe in CI/CD-Tests. |
| NFR-02.3 | CORS ist auf bekannte Origins beschränkt (in Produktion). |

### NFR-03: Wartbarkeit

| ID | Anforderung |
|----|-------------|
| NFR-03.1 | Backend-Testabdeckung: ≥ 80 % für `agents/`, ≥ 90 % für `state.py` und `services/graph_builder.py`. |
| NFR-03.2 | Datenbankmigrationen werden mit Alembic verwaltet. |
| NFR-03.3 | Der LangGraph-Graph wird ab Phase 3 dynamisch aus Blueprint-JSON gebaut (kein hartcodierter Graph in Produktion). |

### NFR-04: Skalierbarkeit

| ID | Anforderung |
|----|-------------|
| NFR-04.1 | LangGraph-Runs werden in asyncio-Thread-Pools ausgeführt, um den FastAPI Event Loop nicht zu blockieren. |
| NFR-04.2 | WebSocket-Sessions sind pro `run_id` isoliert — keine Event-Übertragung zwischen Sessions. |

---

## 6. Technische Abhängigkeiten

| Komponente | Technologie | Version |
|------------|-------------|---------|
| KI-Orchestrierung | LangGraph (Python) | ≥ 0.2.x |
| Backend-API | FastAPI | ≥ 0.110 |
| Frontend-Framework | Next.js + React Flow | Next.js 14+, React Flow 12+ |
| Datenbank | PostgreSQL | 16 |
| Vektor-DB | ChromaDB (lokal) | ≥ 0.5 |
| LLMs | Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o | via API |
| Web-Suche | Tavily Search API | — |
| PDF-Verarbeitung | PyPDF + LangChain Text Splitter | — |

---

## 7. Annahmen und Einschränkungen

### Annahmen

- Nutzer haben gültige API-Keys für Anthropic und/oder OpenAI.
- Die Anwendung wird zunächst lokal (Docker Compose) und später in der Cloud betrieben.
- Ein PDF-Upload ist auf ≤ 50 MB begrenzt.

### Einschränkungen

- Zyklen sind First-Class — der Graph darf nicht zu einem DAG vereinfacht werden.
- State ist die einzige Quelle der Wahrheit — Agents speichern keinen internen Zustand.
- Human-in-the-Loop erfolgt ausschließlich über LangGraphs `interrupt_before` — kein eigener Pause-Mechanismus.
- WebSocket für Echtzeit-Updates ist Pflicht — Polling ist nicht akzeptabel.

---

## 8. Entwicklungs-Roadmap (Phasen)

| Phase | Ziel | Status |
|-------|------|--------|
| Phase 1 — LangGraph Engine (Backend MVP) | Hartcodierter Testgraph, CouncilState, Routing-Logik | ✅ Abgeschlossen |
| Phase 2 — Visueller Baukasten (Frontend MVP) | React Flow Canvas, Custom Nodes/Edges, Blueprint-Parser, PostgreSQL-Speicherung | ✅ Abgeschlossen |
| Phase 3 — Integration (Frontend ↔ Backend) | Dynamischer Graph aus JSON-Blueprint, WebSocket-Events, Frontend-Ausgabe | ✅ Abgeschlossen |
| Phase 4 — Tools & God Mode (Enterprise) | Tavily Search, PyPDF + ChromaDB, Human-in-the-Loop UI | ✅ Abgeschlossen |

---

## 9. Typische Use-Cases

### Use-Case 1: Content-Rat

```
User Input → Master-KI (schreibt Rohfassung)
           → Kritiker-KI (prüft Fakten & SEO)
           → [Wenn Note < 8: zurück zu Master-KI]
           → Lektor-KI (formatiert für Social Media)
```

### Use-Case 2: Programmier-Rat

```
User Input → Architekt-KI (schreibt Code)
           → Tester-KI (sucht Bugs)
           → [Wenn Bugs: zurück zum Architekten]
           → Doku-KI (schreibt das README)
```

### Use-Case 3: Analyse-Rat

```
PDF-Upload → Researcher-KI (liest 100-seitiges PDF)
           → Analyst-KI (extrahiert Kerndaten)
           → Strategie-KI (schreibt Zusammenfassung)
```

---

## 10. Glossar

| Begriff | Definition |
|---------|------------|
| Council | Eine konfigurierte Gruppe von KI-Agents, die zusammenarbeiten |
| Blueprint | Die gespeicherte JSON-Konfiguration eines Councils |
| Council Run | Eine einzelne Ausführung eines Councils |
| CouncilState | Das zentrale TypedDict, das zwischen allen Agents weitergegeben wird |
| God Mode | Ausführungsmodus mit menschlicher Genehmigung an jedem Entscheidungspunkt |
| Auto-Pilot | Ausführungsmodus ohne menschlichen Eingriff |
| Node | Ein einzelner KI-Agent im Graph |
| Edge | Eine Verbindung zwischen zwei Agents (linear oder bedingt) |
| Critic Score | Die numerische Bewertung (0–10) des Kritiker-Agents |
| Route Decision | Das Routing-Signal (`rework`\|`approve`\|benutzerdefiniert) |
