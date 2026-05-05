# JARVIS Units of Work

## Overview

JARVIS is decomposed into **7 units of work**, each representing a logical module within a single deployable application (Python FastAPI backend + React TypeScript frontend). Units are developed in priority order, with each unit building on the foundation established by previous units.

---

## Unit 1: UI Foundation

**Priority**: 1 (first — provides the shell all other units plug into)

**Description**: Establishes the complete application skeleton — FastAPI backend with WebSocket support, React + TypeScript frontend with full layout, and all configuration/data infrastructure. No AI or module logic yet; this unit delivers a working connected shell.

**Backend Modules**:
- `backend/main.py` — FastAPI app, startup/shutdown lifecycle, CORS, static file serving
- `backend/websocket_manager.py` — WebSocket connection management, message envelope, broadcast
- `backend/config_manager.py` — config.json loading, env var overrides, typed property access

**Frontend Components**:
- `frontend/src/App.tsx` — root layout, WebSocket initialization, global state
- `frontend/src/context/WebSocketContext.tsx` — WS context provider and `useWebSocket` hook
- `frontend/src/components/ChatPanel.tsx` — chat UI shell (message display, text input, send button)
- `frontend/src/components/VoiceIndicator.tsx` — voice status indicator (placeholder state)
- `frontend/src/components/StatsSidebar.tsx` — stats sidebar shell (placeholder data)
- `frontend/src/components/NotificationBar.tsx` — notification bar shell (empty state)
- `frontend/src/components/CalendarPanel.tsx` — calendar panel shell (placeholder)

**Data Infrastructure**:
- `data/` directory creation
- `data/conversation_history.json` — initial empty structure
- `data/tasks.json` — initial empty structure
- `config.json` — default configuration values

**Deliverables**:
- Working FastAPI server on port 8000
- React frontend connecting to WebSocket `/ws`
- Single-page layout: chat center, stats sidebar right, notifications top, calendar panel accessible
- Echo WebSocket (messages sent are echoed back) to verify connectivity
- `requirements.txt` and `package.json` with all dependencies

---

## Unit 2: Voice Module

**Priority**: 2

**Description**: Adds full voice I/O capability — microphone capture via `speech_recognition`, text-to-speech via `pyttsx3`, voice mode toggle, and real-time voice status events pushed to the frontend.

**Backend Modules**:
- `backend/voice_module.py` — STT, TTS, voice mode state, WebSocket status events

**Frontend Components**:
- `frontend/src/components/VoiceIndicator.tsx` — animated waveform when listening, speaking indicator, voice toggle button (replaces placeholder from Unit 1)

**Dependencies**: Unit 1 (WebSocketManager, ConfigManager)

**Deliverables**:
- Voice toggle button in UI activates/deactivates voice mode
- Microphone captures audio and transcribes to text
- Transcribed text appears in chat input (ready for Unit 3 to process)
- TTS speaks any text sent to it (tested with hardcoded response until Unit 3)
- Voice status events (`listening_start`, `listening_end`, `speaking_start`, `speaking_end`) update VoiceIndicator in real time
- Graceful fallback to text mode if microphone unavailable

---

## Unit 3: AI Core

**Priority**: 3

**Description**: Integrates the Ollama LLM (llama3.2:3b) for conversational AI, implements LLM-based intent classification and routing, and wires the full chat pipeline end-to-end (text input → intent → AI response → display + speak).

**Backend Modules**:
- `backend/ai_core.py` — Ollama API integration, conversation history (JSON), context window management
- `backend/intent_router.py` — LLM-based intent classification, handler dispatch, response envelope

**Frontend Components**:
- `frontend/src/components/ChatPanel.tsx` — full chat logic (replaces echo; handles `chat_response` messages, renders AI responses)

**Dependencies**: Unit 1 (WebSocketManager, ConfigManager), Unit 2 (VoiceModule for TTS of responses)

**Deliverables**:
- User messages routed through IntentRouter → classified by Ollama → dispatched to handler
- General chat intent handled by AICore with conversation history context
- Conversation history persisted to `data/conversation_history.json` after each exchange
- AI responses displayed in ChatPanel with correct role styling
- If voice mode active, AI responses spoken via VoiceModule.speak()
- Graceful error message if Ollama is unavailable
- Clear history command supported

---

## Unit 4: System Control & Monitoring

**Priority**: 4

**Description**: Adds full OS control capabilities (file management, app launching, shell commands) and real-time system monitoring with battery and network alerts.

**Backend Modules**:
- `backend/system_controller.py` — file ops, app launching, shell commands, confirmation gate
- `backend/system_monitor.py` — psutil polling loop, stats emission, battery/network alert detection

**Frontend Components**:
- `frontend/src/components/StatsSidebar.tsx` — live CPU/RAM/disk/battery/network display (replaces placeholder)
- `frontend/src/components/NotificationBar.tsx` — battery and network alert notifications (replaces placeholder)

**Dependencies**: Unit 1 (WebSocketManager, ConfigManager), Unit 3 (IntentRouter registers system handler)

**Deliverables**:
- System stats (CPU, RAM, disk, battery, network) displayed live in StatsSidebar, updating every 5s
- Battery alerts: charger connected/disconnected, >90% charging, <30% discharging
- Network alerts: Wi-Fi connected/disconnected
- Alerts appear as dismissible notifications in NotificationBar
- System commands via chat: open URL, launch app, list/read/copy/move/delete files, run shell command
- Destructive operations (delete, shell command) trigger confirmation dialog before execution
- Confirmation flow: frontend shows dialog → user confirms → backend executes

---

## Unit 5: Browser Module

**Priority**: 5

**Description**: Adds web search and information retrieval capability using the `browser-use` AI-native framework. Search results are summarized and returned as chat responses.

**Backend Modules**:
- `backend/browser_module.py` — browser-use integration, search execution, result summarization

**Frontend Components**:
- None (results appear as chat responses in ChatPanel)

**Dependencies**: Unit 1 (WebSocketManager, ConfigManager), Unit 3 (IntentRouter registers browser handler)

**Deliverables**:
- User can trigger web search via natural language ("search for...", "find information about...", "what is...")
- browser-use executes search and extracts relevant content
- Summarized result returned as chat response with source URLs
- Graceful error message if browser-use fails or network unavailable

---

## Unit 6: Coding Assistant

**Priority**: 6

**Description**: Adds full IDE-like coding assistance — code generation, explanation, debugging, refactoring, and code review — all powered by the Ollama model with a coding-specific system prompt. Code responses render with syntax highlighting in the chat.

**Backend Modules**:
- `backend/coding_assistant.py` — task type detection, coding system prompt, structured code response

**Frontend Components**:
- `frontend/src/components/ChatPanel.tsx` — code block rendering with syntax highlighting (enhancement to existing component)

**Dependencies**: Unit 1 (WebSocketManager), Unit 3 (AICore, IntentRouter registers coding handler)

**Deliverables**:
- Coding intents (generate, explain, debug, refactor, review) detected and routed to CodingAssistant
- Coding-specific system prompt applied for higher quality code responses
- Responses include language tag, code block, and explanation
- Code blocks rendered with syntax highlighting in ChatPanel
- Works for all common programming languages

---

## Unit 7: Calendar & Task Management

**Priority**: 7

**Description**: Adds local JSON-based calendar and task management — accessible both via natural language chat commands and a dedicated CalendarPanel UI. Includes reminders for tasks due today and tomorrow.

**Backend Modules**:
- `backend/calendar_manager.py` — task CRUD, JSON persistence, reminder queries, REST endpoints

**Frontend Components**:
- `frontend/src/components/CalendarPanel.tsx` — task list display, add/remove UI, date filter, reminders (replaces placeholder)

**Dependencies**: Unit 1 (ConfigManager, REST endpoints), Unit 3 (IntentRouter registers calendar handler)

**Deliverables**:
- Add task via chat: "remind me to X on [date]" or "add task: X for tomorrow"
- Remove task via chat: "remove task X" or "delete reminder X"
- View tasks via chat: "what's on my schedule today/tomorrow/[date]"
- CalendarPanel shows task list with add/remove UI and date filter
- Reminders for today and tomorrow shown in CalendarPanel on load
- Task data persisted to `data/tasks.json` immediately on every change

---

## Code Organization Strategy

```
jarvis/                          # project root
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # Unit 1
│   ├── config_manager.py        # Unit 1
│   ├── websocket_manager.py     # Unit 1
│   ├── voice_module.py          # Unit 2
│   ├── ai_core.py               # Unit 3
│   ├── intent_router.py         # Unit 3
│   ├── system_controller.py     # Unit 4
│   ├── system_monitor.py        # Unit 4
│   ├── browser_module.py        # Unit 5
│   ├── coding_assistant.py      # Unit 6
│   └── calendar_manager.py      # Unit 7
├── frontend/                    # React + TypeScript SPA
│   ├── public/
│   ├── src/
│   │   ├── App.tsx              # Unit 1
│   │   ├── main.tsx             # Unit 1
│   │   ├── context/
│   │   │   └── WebSocketContext.tsx  # Unit 1
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx         # Unit 1 (shell) → Unit 3 (logic) → Unit 6 (code highlight)
│   │   │   ├── VoiceIndicator.tsx    # Unit 1 (shell) → Unit 2 (full)
│   │   │   ├── StatsSidebar.tsx      # Unit 1 (shell) → Unit 4 (full)
│   │   │   ├── NotificationBar.tsx   # Unit 1 (shell) → Unit 4 (full)
│   │   │   └── CalendarPanel.tsx     # Unit 1 (shell) → Unit 7 (full)
│   │   └── types/
│   │       └── index.ts              # Unit 1 — shared TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── data/
│   ├── conversation_history.json
│   └── tasks.json
├── config.json
├── requirements.txt
└── README.md
```
