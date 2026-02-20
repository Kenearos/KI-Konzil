# 🚀 PROJEKT-BLUEPRINT: "CouncilOS" (KI-Rat Baukasten)

**Dokument-Typ:** Master-Product Requirements Document (PRD) & Entwicklungs-Roadmap
**Projekt-Status:** Konzept & Architektur-Briefing für das Dev-Team

---

## 🌟 1. Executive Summary: Sinn und Zweck der App
**Das Problem:** 
Aktuelle KI-Tools (wie ChatGPT) arbeiten linear. Wenn ein Nutzer ein komplexes Ergebnis will (z.B. einen perfekten Blogartikel, rechtssichere PR-Texte oder lauffähigen Code), muss er den Output ständig manuell lesen, Fehler finden und die KI in endlosen Chat-Verläufen korrigieren. Das kostet Zeit und erfordert extrem gutes "Prompting".

**Die Lösung (Unsere App):**
Wir bauen "CouncilOS" – eine visuelle No-Code-Plattform. Anstatt selbst mit der KI zu chatten, baut der Nutzer sich einen eigenen **"KI-Rat" (Multi-Agenten-System)**. 
Der Nutzer definiert verschiedene KI-Experten, gibt ihnen Werkzeuge (Internet, PDF-Reader) und legt per Drag & Drop fest, in welcher Reihenfolge sie Dokumente bearbeiten, kritisieren und überarbeiten. 

**Der USP (Unique Selling Proposition):**
Im Gegensatz zu bestehenden Tools arbeiten unsere KIs in **Endlosschleifen (Zyklen)**. Eine Kritiker-KI kann ein Dokument so lange an die Master-KI zurückweisen, bis es perfekt ist, ohne dass der Mensch eingreifen muss. Wahlweise kann der Mensch als "Vorsitzender des Rates" jeden Schritt abnicken (God-Mode / Human-in-the-Loop).

### Typische Use-Cases (Beispiele für die Devs zum Verständnis):
*   **Der Content-Rat:** Master-KI (schreibt Rohfassung) ➡️ Kritiker-KI (prüft Fakten & SEO) ➡️ *[Bei Fehlern zurück zur Master-KI]* ➡️ Lektor-KI (formatiert für Social Media).
*   **Der Programmier-Rat:** Architekt-KI (schreibt Code) ➡️ Tester-KI (sucht Bugs) ➡️ *[Bei Bugs zurück zum Architekten]* ➡️ Doku-KI (schreibt das Readme).
*   **Der Analyse-Rat:** Researcher-KI (liest 100-seitiges PDF) ➡️ Analyst-KI (extrahiert Kerndaten) ➡️ Strategie-KI (schreibt Zusammenfassung).

---

## 🏗️ 2. Die Technische Architektur (Tech-Stack)
*Liebes Dev-Team, bitte nutzt zwingend diese Technologien, da sie exakt für diesen Use-Case (zyklische Graphen, Multi-Agenten & Human-in-the-loop) gemacht sind:*

*   **KI-Orchestrierung (Das Herzstück):** `LangGraph` (Python). Wir nutzen LangGraph zwingend, weil es im Gegensatz zu alten Frameworks (wie LangChain Agents) echte Zyklen (Loops) erlaubt und eine eingebaute `interrupt_before` (Pause/Human-in-the-Loop) Funktion hat.
*   **Backend-API:** `FastAPI` (Python). Kommuniziert zwischen dem Frontend und dem LangGraph-Backend via WebSockets (für Echtzeit-Updates, welcher Agent gerade arbeitet).
*   **Frontend (Das Visuelle Interface):** `React` oder `Next.js` kombiniert mit **`React Flow`**. React Flow ist der Industriestandard, um interaktive Drag & Drop Canvas-Interfaces (wie Miro oder Zapier) zu bauen.
*   **Datenbank:** `PostgreSQL` (für User-Daten und gespeicherte "Rats-Baupläne" als JSON) + eine simple Vektor-DB wie `ChromaDB` (lokal) oder `Pinecone` für das PDF-Lesewerkzeug.
*   **LLMs:** Integration von `Anthropic Claude 3.5 Sonnet` (Beste Logik/Coding) und `OpenAI GPT-4o` via API.

---

## 🗺️ 3. Visueller Aufbau (UI/UX)
Das Frontend besteht aus zwei Hauptbereichen (Tabs):

### Tab A: Der "Rat-Architekt" (Setup Mode)
Ein Infinite-Canvas (Whiteboard) basierend auf React Flow.
1.  **Nodes (Agenten):** Der User zieht Boxen auf das Feld. Klickt er auf eine Box, öffnet sich ein Menü: Name, System-Prompt (Rolle), LLM-Modell, aktivierte Tools (Toggle-Schalter für Web-Suche, PDF-Reader).
2.  **Edges (Verbindungen):**
    *   *Lineare Pfeile:* Agent A gibt das Dokument stur an Agent B weiter.
    *   *Bedingte Pfeile (Conditional Edges):* Agent A entscheidet selbst (Routing). Z.B. Roter Pfeil (Zurück zur Überarbeitung) / Grüner Pfeil (Weiter zum Lektor).

### Tab B: Das "Konferenzzimmer" (Execution Mode)
Hier wird der gebaute Rat live gestartet.
1.  **Eingabefeld:** Der User tippt den Start-Befehl/Prompt ein oder lädt ein PDF hoch.
2.  **Toggle-Switch:** "Auto-Pilot" (Durchballern im Hintergrund) vs. "God Mode" (Schritt-für-Schritt abklicken).
3.  **Live-View:** Das gebaute Diagramm aus dem Setup wird angezeigt. Der aktuell arbeitende Agent leuchtet auf/pulsiert (via WebSocket).
4.  **Approval-UI (God Mode):** Wenn der Rat pausiert, poppt ein Fenster auf: *"Agent 'Kritiker' schlägt vor, das Dokument an 'Master KI' zurückzugeben. Grund: Zu wenig Details. [Zulassen] [Überschreiben & Weiterleiten]"*.

---

## 📅 4. Die Entwicklungs-Roadmap (Meilensteine)
Wir bauen das Projekt in 4 logischen Phasen. **Wichtig für die Devs:** Wir bauen das Backend (die Logik) zuerst, bevor wir das Frontend (die bunten Boxen) malen.

### 🔴 Phase 1: Die "LangGraph" Engine (Backend MVP)
*Ziel: Beweisen, dass ein iterativer KI-Rat im Code funktioniert, bevor eine UI gebaut wird.*
*   Aufsetzen der Python-Umgebung und FastAPI.
*   Programmieren eines fixen, hardcodierten Graphen in `LangGraph`: `User Input -> Master KI -> Kritiker KI -> (Bedingung: Wenn Note < 8, zurück zu Master KI. Wenn > 8, zu Schriftsteller KI)`.
*   Implementieren der `State`-Logik (Ein Dictionary, das das aktuelle Dokument und Kritikpunkte von Knoten zu Knoten reicht).
*   **Test:** Ausführung und Bestätigung der Schleife über Terminal/Postman.

### 🟡 Phase 2: Der Visuelle Baukasten (Frontend MVP)
*Ziel: Das Drag & Drop Interface bauen und speichern können.*
*   Aufsetzen von `React` und `React Flow`.
*   Entwicklung der Custom Nodes: User können Boxen erstellen, benennen und Prompts eintragen.
*   Entwicklung der Verknüpfungen (Edges ziehen).
*   **Der Parser:** Eine Funktion schreiben, die das grafische `React Flow` Diagramm in ein strukturiertes JSON-Format übersetzt und in der PostgreSQL-Datenbank speichert.

### 🟢 Phase 3: Die Hochzeit (Frontend + Backend)
*Ziel: Die Linien auf dem Bildschirm steuern die echte KI.*
*   Das LangGraph-Backend muss nun dynamisch werden. Es liest das JSON aus Phase 2 und generiert den Graphen *on the fly* im Code.
*   Einrichten von WebSockets: Wenn LangGraph den Knoten "Master KI" betritt, wird ein Event ans Frontend geschickt, damit die Box auf dem Bildschirm gelb aufleuchtet.
*   Darstellung des finalen Text-Outputs im Frontend.

### 🔵 Phase 4: Tools & God Mode (Das High-End Upgrade)
*Ziel: Die App auf Enterprise-Niveau heben.*
*   **Tool-Integration:** Anbindung von `Tavily Search API` (für Web-Suche) und einem PDF-Loader (z.B. `PyPDF` + Vector Store). Zuweisung dieser Tools an spezifische Nodes im Frontend.
*   **Human-in-the-Loop:** Nutzung der `interrupt_before` Methode von LangGraph. Das Backend pausiert und schickt den State an das Frontend. Das Frontend zeigt Buttons (Approve/Reject/Modify). Klickt der User, sendet FastAPI das Signal zurück an LangGraph, um die Ausführung fortzusetzen.

---

## 🛠️ 5. Wichtige Instruktionen an das Dev-Team (Das Datenmodell)

Das Geheimnis dieser App ist der **Global State**, der von LangGraph durch den Rat gewandert wird. Baut die `TypedDict` State-Klasse im Python-Backend ungefähr so auf, damit zyklische Schleifen sauber funktionieren und die KI aus vorherigen Fehlern lernt:

```python
from typing import TypedDict, Annotated, List
import operator

class CouncilState(TypedDict):
    input_topic: str              # Das Ursprungsthema/PDF des Users
    current_draft: str            # Das aktuelle Dokument, an dem gearbeitet wird
    feedback_history: List[str]   # Was Kritiker bisher angemerkt haben (damit sich Fehler in der Schleife nicht wiederholen)
    route_decision: str           # Die Entscheidung der KI (z.B. "rework" oder "approve") zur Steuerung der Edges
    messages: Annotated[list, operator.add] # Der Chatverlauf für die LLMs (System Prompts + Antworten)
    
    jede ki stelle ich ja adhoc für die aufgabe ein (auch wenn ich die speichern können will um eine ähnliche aufgabe mit gleichen parametern nochmal durchlaufen lassen könnte) jede KI und die anzahl derer möchte ich einzeln einstellen ggf lokale.. gf mit api und so.
