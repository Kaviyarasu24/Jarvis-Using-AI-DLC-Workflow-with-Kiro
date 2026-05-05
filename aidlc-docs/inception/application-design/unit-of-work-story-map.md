# JARVIS Unit of Work — Requirements Map

## Requirements to Unit Mapping

### Unit 1: UI Foundation

| Requirement ID | Description |
|---|---|
| FR-070 | Web-based UI (browser-based, Python backend) |
| FR-071 | Chat window with message history display |
| FR-073 | System monitoring stats display (sidebar shell) |
| FR-074 | Alert notifications display (top bar shell) |
| FR-075 | Support both text input and voice input modes (input shell) |
| NFR-023 | Application starts within 5 seconds |
| NFR-030 | Modular code structure |
| NFR-031 | Configuration stored in config file |
| NFR-032 | Clear module interfaces |
| NFR-042 | No hardcoded credentials |
| NFR-050 | Runs on Windows |
| NFR-051 | Python dependencies in requirements.txt |

---

### Unit 2: Voice Module

| Requirement ID | Description |
|---|---|
| FR-010 | Full voice I/O — STT + TTS |
| FR-011 | Voice input via `speech_recognition` |
| FR-012 | Voice output via `pyttsx3` |
| FR-013 | Voice interaction toggleable |
| FR-014 | Visual waveform/indicator when voice active |
| NFR-002 | Voice recognition processes audio within 2 seconds |
| NFR-011 | Handle microphone unavailability gracefully |
| NFR-021 | Voice and text modes clearly indicated in UI |

---

### Unit 3: AI Core

| Requirement ID | Description |
|---|---|
| FR-001 | Conversational chat powered by Ollama (llama3.2:3b) |
| FR-002 | Send messages to Ollama API, display responses |
| FR-003 | Persistent conversation history in JSON |
| FR-004 | Load history on startup, save after each interaction |
| FR-005 | Context-aware responses using conversation history |
| NFR-001 | AI response latency target < 10s |
| NFR-010 | Handle Ollama unavailability gracefully |
| NFR-013 | Conversation history not lost on shutdown (write-on-update) |

---

### Unit 4: System Control & Monitoring

| Requirement ID | Description |
|---|---|
| FR-040 | Full system control: apps, files, shell commands |
| FR-041 | Open URLs in default browser |
| FR-042 | Launch installed applications by name |
| FR-043 | Read, list, copy, move, delete files/directories |
| FR-044 | Execute shell commands, return output to chat |
| FR-045 | Destructive operations require explicit confirmation |
| FR-050 | Monitor CPU, RAM, disk usage in real time |
| FR-051 | Proactive alerts when thresholds exceeded |
| FR-052 | Monitor running processes |
| FR-053 | Battery alerts: charger connected/disconnected |
| FR-053a | Battery alert: charger connected |
| FR-053b | Battery alert: charger disconnected |
| FR-053c | Battery alert: >90% while charging |
| FR-053d | Battery alert: <30% while not charging |
| FR-054 | Network alerts: Wi-Fi connected/disconnected |
| FR-054a | Network alert: Wi-Fi connected |
| FR-054b | Network alert: Wi-Fi disconnected |
| FR-055 | Alerts displayed as non-intrusive notifications |
| NFR-003 | System stats refresh at configurable interval (default 5s) |
| NFR-004 | Battery/network monitoring polls at minimum 10s |
| NFR-041 | Destructive operations require user confirmation |

---

### Unit 5: Browser Module

| Requirement ID | Description |
|---|---|
| FR-030 | Web search and information retrieval |
| FR-031 | Browser automation via `browser-use` |
| FR-032 | Extract and summarize web content in chat |
| FR-033 | Web search triggered by user intent |
| NFR-012 | Handle browser-use failures gracefully |

---

### Unit 6: Coding Assistant

| Requirement ID | Description |
|---|---|
| FR-020 | Full coding assistance: generate, explain, debug, refactor, review |
| FR-021 | Coding assistance powered by Ollama (llama3.2:3b) |
| FR-022 | Detect coding-related queries, apply coding system prompt |
| FR-023 | Code responses rendered with syntax highlighting |
| FR-024 | No code execution — generation only |

---

### Unit 7: Calendar & Task Management

| Requirement ID | Description |
|---|---|
| FR-060 | JSON-based local calendar and task management |
| FR-061 | Add tasks with title, date, optional description |
| FR-062 | Remove tasks by ID or title |
| FR-063 | View tasks: all, today, tomorrow, specific date |
| FR-064 | Reminders for tasks due today and tomorrow |
| FR-065 | Calendar/task data persisted in local JSON |
| NFR-013 | Task data not lost on shutdown (write-on-update) |

---

## Coverage Summary

| Unit | Requirements Covered | NFRs Covered |
|---|---|---|
| Unit 1 — UI Foundation | FR-070, FR-071, FR-073, FR-074, FR-075 | NFR-023, NFR-030, NFR-031, NFR-032, NFR-042, NFR-050, NFR-051 |
| Unit 2 — Voice Module | FR-010, FR-011, FR-012, FR-013, FR-014 | NFR-002, NFR-011, NFR-021 |
| Unit 3 — AI Core | FR-001, FR-002, FR-003, FR-004, FR-005 | NFR-001, NFR-010, NFR-013 |
| Unit 4 — System Control & Monitoring | FR-040 to FR-055 (15 FRs) | NFR-003, NFR-004, NFR-041 |
| Unit 5 — Browser Module | FR-030, FR-031, FR-032, FR-033 | NFR-012 |
| Unit 6 — Coding Assistant | FR-020, FR-021, FR-022, FR-023, FR-024 | — |
| Unit 7 — Calendar & Tasks | FR-060, FR-061, FR-062, FR-063, FR-064, FR-065 | NFR-013 (shared) |

**Total**: 40 functional requirements + 14 NFRs — all requirements covered across 7 units.

**NFRs covered across all units** (not unit-specific):
- NFR-020 (intuitive UI) — Unit 1
- NFR-022 (dismissible alerts) — Unit 4
- NFR-040 (security extension N/A) — N/A
