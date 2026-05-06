# JARVIS — Project Analysis

> AI-Powered Personal Assistant | Python FastAPI + React TypeScript | Local LLM via Ollama

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Backend Modules](#5-backend-modules)
6. [Frontend Components](#6-frontend-components)
7. [Features by Unit](#7-features-by-unit)
8. [Communication Protocol](#8-communication-protocol)
9. [Data & Configuration](#9-data--configuration)
10. [Testing](#10-testing)
11. [Setup & Running](#11-setup--running)
12. [Post-Completion Enhancements](#12-post-completion-enhancements)
13. [Development Status](#13-development-status)

---

## 1. Project Overview

JARVIS is a fully local, AI-powered personal assistant that runs entirely on the user's machine — no cloud services required. It integrates conversational AI, voice I/O, coding assistance, browser automation, system control, and task management into a single unified application.

| Attribute | Value |
|---|---|
| **Project Type** | Greenfield — single-user desktop assistant |
| **Deployment Target** | Local (Windows primary; Linux/macOS compatible) |
| **AI Engine** | Ollama — `llama3.2:3b` (local LLM inference) |
| **Backend** | Python 3.11+ / FastAPI |
| **Frontend** | React 18 / TypeScript / Vite |
| **Communication** | WebSocket (real-time) + REST (CRUD) |
| **Storage** | Local JSON files |
| **Build Units** | 7 units + 13 post-completion enhancements |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React SPA (Port 5173 / 8000)                │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────┐  │
│  │ChatPanel │  │VoiceIndicator│  │StatsSide │  │CalendarPnl│  │
│  └──────────┘  └──────────────┘  └──────────┘  └───────────┘  │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐                  │
│  │JarvisRing│  │NotificationBr│  │NewsPanel │                  │
│  └──────────┘  └──────────────┘  └──────────┘                  │
│                  WebSocketContext (shared state)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ WebSocket /ws  +  REST /api/*
┌────────────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                     │
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐    │
│  │ IntentRouter │──▶│   AICore     │──▶│  Ollama API      │    │
│  └──────┬───────┘   └──────────────┘   │  llama3.2:3b     │    │
│         │                              └──────────────────┘    │
│    ┌────▼──────────────────────────────────────────────────┐   │
│    │  Module Dispatch                                       │   │
│    │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │   │
│    │  │VoiceModule  │  │SystemControl │  │BrowserModule│  │   │
│    │  └─────────────┘  └──────────────┘  └─────────────┘  │   │
│    │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  │   │
│    │  │CodingAssist │  │CalendarMgr   │  │SystemMonitor│  │   │
│    │  └─────────────┘  └──────────────┘  └─────────────┘  │   │
│    └───────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │WebSocketMgr  │  │ConfigManager │  │NewsModule / DataInit │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │   data/             │
              │  conversation_      │
              │  history.json       │
              │  tasks.json         │
              └─────────────────────┘
```

**Key architectural decisions:**

- **Modular backend** — each capability lives in its own Python module with a clean interface
- **Intent-based routing** — the LLM classifies user intent, then dispatches to the right handler
- **Single WebSocket connection** — multiplexes chat, stats, alerts, voice status, and task updates
- **Async-first** — FastAPI async/await throughout for non-blocking I/O
- **Graceful degradation** — fallbacks for Ollama unavailability, missing microphone, browser-use failures
- **Configuration-driven** — all thresholds, intervals, and model settings in `config.json`

---

## 3. Tech Stack

### Backend

| Library | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| FastAPI | ≥0.115.0 | Web framework, WebSocket, REST |
| Uvicorn | ≥0.29.0 | ASGI server |
| Pydantic | ≥2.10.4 | Data validation and settings |
| httpx | ≥0.27.2 | Async HTTP client (Ollama API) |
| psutil | 5.9.8 | System stats (CPU, RAM, disk, battery) |
| SpeechRecognition | 3.10.4 | Speech-to-text (STT) |
| pyttsx3 | 2.90 | Text-to-speech (TTS) |
| PyAudio | 0.2.14 | Microphone audio capture |
| browser-use | 0.1.40 | AI-native web automation |
| pycaw | 20240210 | Windows volume/audio control |
| comtypes | ≥1.4.1 | Windows COM interface (pycaw dependency) |
| pytest | 8.2.0 | Unit testing |
| pytest-asyncio | 0.23.6 | Async test support |

### Frontend

| Library | Version | Purpose |
|---|---|---|
| React | 18.3.1 | UI framework |
| TypeScript | 5.4.5 | Type safety |
| Vite | 5.2.11 | Build tool and dev server |
| Tailwind CSS | 3.4.3 | Utility-first styling |
| Lucide React | 0.378.0 | Icon library |
| react-syntax-highlighter | 15.5.0 | Code block rendering with syntax highlighting |

### Infrastructure

| Tool | Purpose |
|---|---|
| Ollama | Local LLM inference server |
| llama3.2:3b | Language model (chat, intent classification, coding) |
| Node.js 18+ | Frontend build toolchain |
| npm | Package management |
| ESLint + TypeScript ESLint | Code linting |

---

## 4. Project Structure

```
jarvis/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point, lifecycle, routes
│   ├── config_manager.py        # config.json loading, env var overrides
│   ├── websocket_manager.py     # WebSocket connection pool, broadcast
│   ├── data_init.py             # data/ directory and file initialization
│   ├── ai_core.py               # Ollama integration, conversation history
│   ├── intent_router.py         # LLM intent classification, handler dispatch
│   ├── voice_module.py          # STT (speech_recognition) + TTS (pyttsx3)
│   ├── system_controller.py     # File ops, app launch, shell commands
│   ├── system_monitor.py        # CPU/RAM/disk stats, battery/network alerts
│   ├── browser_module.py        # Web search via browser-use
│   ├── coding_assistant.py      # Code generation, debug, refactor, review
│   ├── calendar_manager.py      # Task CRUD, reminders, natural language parsing
│   ├── news_module.py           # Google News RSS fetching and parsing
│   └── tests/
│       ├── test_ai_core.py
│       ├── test_browser_module.py
│       ├── test_calendar_manager.py
│       ├── test_coding_assistant.py
│       ├── test_config_manager.py
│       ├── test_intent_router.py
│       ├── test_system_controller.py
│       ├── test_voice_module.py
│       └── test_websocket_manager.py
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Root layout, status indicators, WebSocket init
│   │   ├── main.tsx             # React entry point
│   │   ├── index.css            # Global styles, animations
│   │   ├── context/
│   │   │   └── WebSocketContext.tsx   # WS state provider + useWebSocket hook
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx          # Chat UI, message list, input bar
│   │   │   ├── VoiceIndicator.tsx     # Waveform animation, voice toggle
│   │   │   ├── StatsSidebar.tsx       # CPU/RAM/disk progress bars
│   │   │   ├── NotificationBar.tsx    # Toast notification pills
│   │   │   ├── CalendarPanel.tsx      # Task list, add/complete/delete
│   │   │   ├── JarvisRing.tsx         # Arc reactor animation (4 rings)
│   │   │   └── NewsPanel.tsx          # News feed, 7 topic categories
│   │   └── types/
│   │       └── index.ts               # Shared TypeScript interfaces
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── data/                        # Auto-created at startup
│   ├── conversation_history.json
│   └── tasks.json
│
├── config.json                  # Application configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── README.md
```

---

## 5. Backend Modules

### `main.py` — Application Entry Point
- FastAPI app initialization with CORS and static file serving
- WebSocket endpoint `/ws` — accepts connections, routes messages
- REST endpoints: `/api/tasks` (CRUD), `/api/health`, `/api/clear-history`
- Startup/shutdown lifecycle hooks (data init, monitor start/stop)

### `config_manager.py` — Configuration
- Loads `config.json` at startup
- Supports environment variable overrides with `JARVIS_` prefix
- Typed property access for all config values

### `websocket_manager.py` — WebSocket Pool
- Manages active WebSocket connections
- Broadcast to all connected clients
- Consistent message envelope: `{ "type": "...", "payload": { ... } }`

### `ai_core.py` — Ollama Integration
- Sends requests to Ollama REST API (`/api/chat`)
- Maintains conversation history (loaded from / saved to JSON)
- Context window management (last N messages)
- Module-specific system prompts (general chat vs. coding vs. intent)
- Streaming token delivery support
- Graceful error handling when Ollama is unavailable

### `intent_router.py` — Intent Classification & Routing
- Sends user message to Ollama with intent-classification system prompt
- Parses classified intent: `chat | code | search | system | calendar | voice_control`
- Dispatches to the correct module handler
- Keyword-based fallback if LLM classification fails
- Returns structured response envelope to WebSocket layer

### `voice_module.py` — Voice I/O
- STT: captures microphone audio via `speech_recognition`, transcribes with Google STT or offline engine
- TTS: speaks text via `pyttsx3` at configurable rate
- Voice mode state management (active/inactive toggle)
- Emits WebSocket events: `listening_start`, `listening_end`, `speaking_start`, `speaking_end`
- Graceful fallback to text mode if microphone unavailable

### `system_controller.py` — OS Control
- Open URLs in default browser
- Launch installed applications by name
- File operations: list, read, copy, move, delete (delete requires confirmation flag)
- Shell command execution with stdout/stderr capture
- Confirmation gate for all destructive operations

### `system_monitor.py` — System Monitoring & Alerts
- Polls CPU, RAM, and disk usage at configurable interval (default: 5s)
- Polls battery level and charging state (default: 10s)
- Monitors network/Wi-Fi connectivity
- Transition-based alert system (fires once on state change, not repeatedly):
  - Charger connected / disconnected
  - Battery > 90% while charging
  - Battery < 30% while discharging
  - Wi-Fi connected / disconnected
  - CPU above threshold (default: 90%)
- Broadcasts stats and alerts over WebSocket

### `browser_module.py` — Web Automation
- Accepts natural language search queries or URLs
- Executes web search via `browser-use` AI-native framework
- Extracts and summarizes relevant content from results
- Returns structured summary to chat
- Graceful degradation on browser-use failures

### `coding_assistant.py` — Coding Assistance
- Detects coding task type: `generate | explain | debug | refactor | review`
- Applies task-specific system prompts for higher quality responses
- Formats responses with language-tagged code blocks
- Returns structured response: `{ language, code, explanation }`
- Supports all common programming languages

### `calendar_manager.py` — Task Management
- JSON-based task storage with atomic writes
- CRUD operations: create, read, update, delete tasks
- Natural language date parsing ("remind me to X on Friday")
- Task filtering: all, today, tomorrow, specific date
- Reminder detection for tasks due today or tomorrow

### `news_module.py` — News Feed
- Fetches headlines from Google News RSS
- Supports 7 topic categories (technology, science, business, health, sports, entertainment, world)
- Auto-refresh every 5 minutes
- Returns structured article list to frontend

### `data_init.py` — Data Initialization
- Creates `data/` directory on startup if it doesn't exist
- Initializes `conversation_history.json` and `tasks.json` with empty structures

---

## 6. Frontend Components

### `App.tsx` — Root Layout
- Defines the overall page layout (JARVIS ring background, floating panels)
- Initializes WebSocket connection on mount
- Displays server and Ollama status indicators (polling `/api/health`)
- Manages global notification state

### `WebSocketContext.tsx` — State Management
- React Context provider wrapping the entire app
- Exposes `useWebSocket()` hook for all components
- Handles WebSocket message routing to appropriate state slices
- Manages connection lifecycle (connect, reconnect, disconnect)

### `ChatPanel.tsx` — Chat Interface
- Floating right-side card layout
- Message list with role-based styling (user / assistant)
- Message timestamps (HH:MM format)
- Hover-reveal copy button per message
- Message delete functionality
- Syntax-highlighted code blocks via `react-syntax-highlighter`
- Floating input bar (collapses to mic icon, expands on hover/focus)
- Stop generation button during active AI response
- Streaming token-by-token response display

### `VoiceIndicator.tsx` — Voice Status
- Animated waveform when microphone is listening
- Speaking indicator during TTS playback
- Voice mode toggle button
- Responds to WebSocket voice status events

### `StatsSidebar.tsx` — System Stats
- Real-time CPU, RAM, and disk usage progress bars
- Color-coded thresholds (green → yellow → red)
- Updates on every stats WebSocket message (every 5s)

### `NotificationBar.tsx` — Toast Notifications
- Android 15-style center-top pill notifications
- Displays battery, network, CPU, and volume alerts
- Auto-dismiss after configurable duration
- Stacks multiple simultaneous notifications

### `CalendarPanel.tsx` — Task Management
- Task list with completion checkboxes
- Add new task with natural language input
- Delete tasks
- Filter by date (today, tomorrow, all)
- Syncs with backend via REST API (`/api/tasks`)

### `JarvisRing.tsx` — Arc Reactor Animation
- 4 concentric rotating rings as background centerpiece
- Pulses and changes color when AI is processing a response
- Idle animation when waiting for input

### `NewsPanel.tsx` — News Feed
- Floating left-side card
- 7 topic category tabs
- Article list with title, source, and timestamp
- Auto-refreshes every 5 minutes via WebSocket or polling

---

## 7. Features by Unit

| Unit | Status | Key Deliverables |
|---|---|---|
| **1 — UI Foundation** | ✅ Complete | FastAPI server, React SPA shell, WebSocket connectivity, config system, data directory |
| **2 — Voice Module** | ✅ Complete | STT via speech_recognition, TTS via pyttsx3, voice toggle, waveform indicator, graceful fallback |
| **3 — AI Core** | ✅ Complete | Ollama integration, intent classification, conversation history, context window, streaming responses |
| **4 — System Control** | ✅ Complete | File ops, app launch, shell commands, CPU/RAM/disk monitoring, battery/network alerts |
| **5 — Browser Module** | ✅ Complete | Web search via browser-use, content extraction, summarization, graceful degradation |
| **6 — Coding Assistant** | ✅ Complete | Code generation/explain/debug/refactor/review, task-specific prompts, syntax highlighting |
| **7 — Calendar & Tasks** | ✅ Complete | Task CRUD, natural language date parsing, reminders, REST API, CalendarPanel UI |

---

## 8. Communication Protocol

### WebSocket Message Envelope

All WebSocket messages use a consistent envelope format:

```json
{
  "type": "<message_type>",
  "payload": { ... }
}
```

### Message Types (Backend → Frontend)

| Type | Payload | Description |
|---|---|---|
| `chat_response` | `{ message, role, timestamp }` | AI response text |
| `chat_token` | `{ token }` | Streaming token during generation |
| `chat_done` | `{}` | Signals end of streaming response |
| `system_stats` | `{ cpu, ram, disk }` | System resource usage |
| `battery_alert` | `{ level, charging, message }` | Battery state change alert |
| `network_alert` | `{ connected, message }` | Network state change alert |
| `cpu_alert` | `{ cpu_percent, message }` | CPU threshold exceeded |
| `volume_alert` | `{ volume, muted, message }` | Volume/mute state change |
| `voice_status` | `{ status }` | `listening_start/end`, `speaking_start/end` |
| `task_update` | `{ tasks }` | Task list after CRUD operation |
| `news_update` | `{ articles, category }` | News feed refresh |
| `error` | `{ message }` | Error notification |

### Message Types (Frontend → Backend)

| Type | Payload | Description |
|---|---|---|
| `user_message` | `{ text }` | User chat input |
| `voice_toggle` | `{ active }` | Enable/disable voice mode |
| `stop_generation` | `{}` | Cancel active AI response |
| `clear_history` | `{}` | Clear conversation history |

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Server and Ollama status check |
| `GET` | `/api/tasks` | List all tasks |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/{id}` | Update a task |
| `DELETE` | `/api/tasks/{id}` | Delete a task |
| `POST` | `/api/clear-history` | Clear conversation history |

---

## 9. Data & Configuration

### `config.json`

```json
{
  "ollama_model": "llama3.2:3b",
  "ollama_base_url": "http://127.0.0.1:11434",
  "stats_interval_seconds": 5,
  "battery_interval_seconds": 10,
  "cpu_alert_threshold": 90.0,
  "history_context_window": 5,
  "backend_port": 8000,
  "data_dir": "./data",
  "voice_timeout_seconds": 5,
  "voice_phrase_limit_seconds": 10,
  "tts_rate": 175
}
```

All values can be overridden with environment variables using the `JARVIS_` prefix (e.g., `JARVIS_OLLAMA_MODEL`, `JARVIS_PORT`).

### Data Files

| File | Format | Contents |
|---|---|---|
| `data/conversation_history.json` | JSON array | Chat messages with role and timestamp |
| `data/tasks.json` | JSON array | Tasks with id, title, due date, completion status |

Both files are written atomically after every change to prevent data loss on crash.

---

## 10. Testing

### Test Coverage

| Test File | Module Under Test | Focus Areas |
|---|---|---|
| `test_ai_core.py` | `ai_core.py` | Ollama API calls, history management, context window |
| `test_browser_module.py` | `browser_module.py` | Search execution, error handling, result parsing |
| `test_calendar_manager.py` | `calendar_manager.py` | CRUD operations, date parsing, reminders |
| `test_coding_assistant.py` | `coding_assistant.py` | Task detection, prompt selection, response formatting |
| `test_config_manager.py` | `config_manager.py` | Config loading, env var overrides, defaults |
| `test_intent_router.py` | `intent_router.py` | Intent classification, dispatch, fallback |
| `test_system_controller.py` | `system_controller.py` | File ops, app launch, confirmation gate |
| `test_voice_module.py` | `voice_module.py` | STT/TTS, voice mode state, fallback |
| `test_websocket_manager.py` | `websocket_manager.py` | Connection management, broadcast, envelope |

**Total**: 106+ unit tests across 9 modules

### Running Tests

```bash
# From jarvis/ directory
pytest backend/tests/ -v

# Run a specific test file
pytest backend/tests/test_coding_assistant.py -v

# Run with coverage (if pytest-cov installed)
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

### Performance Targets

| Operation | Target |
|---|---|
| AI response (first token) | < 10 seconds |
| Voice transcription | < 2 seconds |
| System stats refresh | Every 5 seconds |
| Battery/network poll | Every 10 seconds |
| News feed refresh | Every 5 minutes |

---

## 11. Setup & Running

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running
- Ollama model: `ollama pull llama3.2:3b`
- Microphone (for voice features)
- Windows (primary target; Linux/macOS compatible with minor adjustments)

### Backend Setup

```bash
# From jarvis/ directory
pip install -r requirements.txt

# Start the backend
python -m backend.main
# Runs at http://localhost:8000
```

### Frontend — Development Mode

```bash
# From jarvis/frontend/ directory
npm install
npm run dev
# Runs at http://localhost:5173 (proxies API to :8000)
```

### Frontend — Production Build

```bash
# From jarvis/frontend/ directory
npm run build
# Output: jarvis/frontend/dist/
# FastAPI serves the built files automatically at http://localhost:8000
```

### Verify Setup

1. Open `http://localhost:8000` (or `http://localhost:5173` in dev mode)
2. Check the status indicators in the UI — server and Ollama should both show green
3. Type a message in the chat input and press Enter
4. JARVIS should respond via the Ollama model

---

## 12. Post-Completion Enhancements

After the initial 7 units were completed, 13 additional features were implemented:

| # | Feature | Description |
|---|---|---|
| 1 | **Streaming responses** | AI responses delivered token-by-token for real-time display |
| 2 | **Message timestamps** | HH:MM timestamp displayed on each chat message |
| 3 | **Copy button** | Hover-reveal copy-to-clipboard button per message |
| 4 | **Stop generation** | Button to cancel an active AI response mid-stream |
| 5 | **Message delete** | Remove individual messages from the chat history |
| 6 | **LLM intent extraction** | Keyword fallback when LLM intent classification is uncertain |
| 7 | **Toast notifications** | Android 15-style center-top pill alerts for system events |
| 8 | **Volume/mute monitoring** | Alerts when system volume or mute state changes |
| 9 | **JARVIS ring animation** | 4 concentric rotating rings; pulses during AI processing |
| 10 | **Status indicators** | Server and Ollama health shown in UI via WebSocket + polling |
| 11 | **Floating input bar** | Collapses to mic icon, expands on hover/focus |
| 12 | **News panel** | Left-side floating card with 7 topic categories, auto-refresh |
| 13 | **UI layout redesign** | Chat as floating right card, JARVIS ring as background, news on left |

---

## 13. Development Status

### Phase Progress

| Phase | Status |
|---|---|
| Inception (requirements, design, planning) | ✅ Complete |
| Construction — Unit 1: UI Foundation | ✅ Complete |
| Construction — Unit 2: Voice Module | ✅ Complete |
| Construction — Unit 3: AI Core | ✅ Complete |
| Construction — Unit 4: System Control | ✅ Complete |
| Construction — Unit 5: Browser Module | ✅ Complete |
| Construction — Unit 6: Coding Assistant | ✅ Complete |
| Construction — Unit 7: Calendar & Tasks | ✅ Complete |
| Post-completion enhancements (13 features) | ✅ Complete |
| Build & Test instructions | ✅ Complete |
| Operations / Deployment | 🟡 Placeholder (local app, no deployment needed) |

### Requirements Coverage

| Category | Count | Status |
|---|---|---|
| Functional Requirements | 76 | ✅ All implemented |
| Non-Functional Requirements | 51 | ✅ All addressed |
| Extensions (Security Baseline) | — | Opted out |
| Extensions (Property-Based Testing) | — | Opted out |

---

*Generated: 2026-05-05 | JARVIS v1.0.0*
