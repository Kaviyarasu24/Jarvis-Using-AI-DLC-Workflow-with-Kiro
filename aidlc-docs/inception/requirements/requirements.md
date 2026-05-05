# JARVIS Requirements Document

## Intent Analysis Summary

| Attribute | Value |
|---|---|
| **User Request** | Build JARVIS — an AI-powered personal assistant integrating voice, coding assistance, browser automation, and system control |
| **Request Type** | New Project (Greenfield) |
| **Scope Estimate** | System-wide — multiple integrated modules |
| **Complexity Estimate** | Complex — multi-capability platform with AI, voice, UI, system, and browser components |
| **Depth Level** | Comprehensive |

---

## 1. Functional Requirements

### 1.1 Core AI Chat Assistant

| ID | Requirement |
|---|---|
| FR-001 | JARVIS shall provide a conversational chat interface powered by a local Ollama model (llama3.2:3b) |
| FR-002 | JARVIS shall send user messages to the Ollama API and display AI-generated responses in the chat UI |
| FR-003 | JARVIS shall maintain persistent conversation history stored locally in JSON format |
| FR-004 | Conversation history shall be loaded on startup and saved after each interaction |
| FR-005 | JARVIS shall support context-aware responses by including recent conversation history in each prompt |

### 1.2 Voice Interaction

| ID | Requirement |
|---|---|
| FR-010 | JARVIS shall support full voice I/O — voice input (speech-to-text) and voice output (text-to-speech) |
| FR-011 | Voice input shall use the Python `speech_recognition` library to capture and transcribe microphone audio |
| FR-012 | Voice output shall use the `pyttsx3` library to speak AI responses aloud |
| FR-013 | Voice interaction shall be toggleable — users can switch between voice and text modes |
| FR-014 | The UI shall display a visual waveform or indicator when voice input is active |

### 1.3 Coding Assistance

| ID | Requirement |
|---|---|
| FR-020 | JARVIS shall provide full IDE-like coding assistance: code generation, explanation, debugging, refactoring, and code review |
| FR-021 | All coding assistance shall be powered by the same local Ollama model (llama3.2:3b) |
| FR-022 | JARVIS shall detect when a user query is coding-related and apply a coding-specific system prompt |
| FR-023 | Code responses shall be rendered with syntax highlighting in the chat UI |
| FR-024 | JARVIS shall NOT execute generated code — code generation only |

### 1.4 Browser Automation (Web Search & Information Retrieval)

| ID | Requirement |
|---|---|
| FR-030 | JARVIS shall support basic web search and information retrieval from the internet |
| FR-031 | Browser automation shall use the `browser-use` AI-native framework |
| FR-032 | JARVIS shall extract and summarize relevant information from web pages and present it in the chat |
| FR-033 | Web search shall be triggered by user intent (e.g., "search for...", "find information about...") |

### 1.5 System Control

| ID | Requirement |
|---|---|
| FR-040 | JARVIS shall support full system control: open applications, manage files, run shell commands, and control OS settings |
| FR-041 | JARVIS shall be able to open URLs in the default browser |
| FR-042 | JARVIS shall be able to launch installed applications by name |
| FR-043 | JARVIS shall be able to read, list, copy, move, and delete files/directories (with user confirmation for destructive operations) |
| FR-044 | JARVIS shall be able to execute shell/terminal commands and return output to the chat |
| FR-045 | Destructive system operations (file deletion, command execution) shall require explicit user confirmation |

### 1.6 System Monitoring & Alerts

| ID | Requirement |
|---|---|
| FR-050 | JARVIS shall monitor and display real-time system stats: CPU usage, RAM usage, disk usage |
| FR-051 | JARVIS shall provide proactive alerts when system thresholds are exceeded (e.g., high CPU) |
| FR-052 | JARVIS shall monitor running processes |
| FR-053 | JARVIS shall monitor battery status and trigger alerts for: |
| FR-053a | — Charger connected |
| FR-053b | — Charger disconnected |
| FR-053c | — Battery above 90% while charging |
| FR-053d | — Battery below 30% while not charging |
| FR-054 | JARVIS shall monitor network status and trigger alerts for: |
| FR-054a | — Wi-Fi connected |
| FR-054b | — Wi-Fi disconnected |
| FR-055 | Alerts shall be displayed as non-intrusive notifications in the UI |

### 1.7 Calendar & Task Management

| ID | Requirement |
|---|---|
| FR-060 | JARVIS shall provide a JSON-based local calendar and task management system |
| FR-061 | Users shall be able to add tasks/events with a title, date, and optional description |
| FR-062 | Users shall be able to remove tasks/events by ID or title |
| FR-063 | Users shall be able to view all tasks, today's tasks, tomorrow's tasks, or tasks on a specific date |
| FR-064 | JARVIS shall provide reminders for tasks due today and tomorrow |
| FR-065 | Calendar/task data shall be persisted in a local JSON file |

### 1.8 User Interface

| ID | Requirement |
|---|---|
| FR-070 | JARVIS shall have a web-based UI (browser-based, Python backend serving a frontend) |
| FR-071 | The UI shall include a chat window with message history display |
| FR-072 | The UI shall include a voice waveform/visual indicator for active voice input |
| FR-073 | The UI shall display system monitoring stats (CPU, RAM, disk) in a sidebar or panel |
| FR-074 | The UI shall display alert notifications for battery and network events |
| FR-075 | The UI shall support both text input and voice input modes |
| FR-076 | Code responses shall be rendered with syntax highlighting |

---

## 2. Non-Functional Requirements

### 2.1 Performance

| ID | Requirement |
|---|---|
| NFR-001 | AI response latency shall be acceptable for local model inference (llama3.2:3b on Ollama) — target < 10s for typical queries |
| NFR-002 | Voice recognition shall process audio input within 2 seconds of speech completion |
| NFR-003 | System monitoring stats shall refresh at a configurable interval (default: every 5 seconds) |
| NFR-004 | Battery and network monitoring shall poll at a minimum interval of 10 seconds |

### 2.2 Reliability

| ID | Requirement |
|---|---|
| NFR-010 | JARVIS shall handle Ollama API unavailability gracefully with a clear error message |
| NFR-011 | JARVIS shall handle microphone unavailability gracefully (fall back to text input) |
| NFR-012 | JARVIS shall handle browser-use failures gracefully with a fallback error message |
| NFR-013 | Conversation history and task data shall not be lost on unexpected application shutdown (write-on-update) |

### 2.3 Usability

| ID | Requirement |
|---|---|
| NFR-020 | The UI shall be intuitive and require no technical knowledge to operate |
| NFR-021 | Voice and text modes shall be clearly indicated in the UI |
| NFR-022 | System alerts shall be non-intrusive and dismissible |
| NFR-023 | The application shall start up within 5 seconds on a standard developer machine |

### 2.4 Maintainability

| ID | Requirement |
|---|---|
| NFR-030 | Code shall be modular — each capability (voice, coding, browser, system, calendar) in its own module |
| NFR-031 | Configuration (Ollama model name, monitoring intervals, thresholds) shall be stored in a config file |
| NFR-032 | All modules shall have clear interfaces to allow future extension |

### 2.5 Security (PoC/Prototype Level)

| ID | Requirement |
|---|---|
| NFR-040 | Security extension rules are NOT enforced (user opted out — PoC/prototype project) |
| NFR-041 | Destructive system operations shall require explicit user confirmation as a basic safety measure |
| NFR-042 | No sensitive credentials shall be hardcoded — use environment variables or config files |

### 2.6 Portability

| ID | Requirement |
|---|---|
| NFR-050 | JARVIS shall run on Windows (primary target based on user environment) |
| NFR-051 | Python dependencies shall be managed via `requirements.txt` |

---

## 3. Technology Stack

| Component | Technology |
|---|---|
| **Backend Language** | Python |
| **AI/LLM** | Ollama (local) — model: `llama3.2:3b` |
| **Voice Input (STT)** | Python `speech_recognition` library |
| **Voice Output (TTS)** | `pyttsx3` library |
| **Web Framework** | FastAPI (Python backend, REST API) |
| **Frontend** | React + TypeScript (served separately or via FastAPI static files) |
| **Browser Automation** | `browser-use` (AI-native) |
| **System Monitoring** | `psutil` library |
| **Battery Monitoring** | `psutil` (battery info) |
| **Network Monitoring** | `psutil` / socket checks |
| **Conversation Memory** | Local JSON file |
| **Calendar/Tasks** | Local JSON file |
| **Testing** | Standard unit tests (PBT not enforced) |

---

## 4. Development Priority Order

As specified by the user:

1. **UI** — Web-based chat interface with voice waveform
2. **Voice** — Speech recognition input + TTS output
3. **Chat/AI Core** — Ollama integration, conversation history, context management
4. **System Control** — File management, app launching, shell commands, system monitoring & alerts
5. **Browser** — Web search and information retrieval via browser-use
6. **Coding Assistance** — Code generation, explanation, debugging, refactoring, review
7. **Remaining** — Calendar/task management, reminders

---

## 5. MVP Scope

Full feature set as described — all capabilities included in the initial version (user selected option D).

---

## 6. Extension Configuration

| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No | Requirements Analysis |
| Property-Based Testing | No | Requirements Analysis |

---

## 7. Out of Scope

- Multi-user support (single-user personal assistant only)
- Cloud deployment or SaaS model
- Mobile application
- Code execution / sandboxed runtime
- External calendar integrations (Google Calendar, Outlook)
- External communication tools (Slack, email)
