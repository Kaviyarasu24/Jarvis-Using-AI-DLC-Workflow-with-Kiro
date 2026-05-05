# JARVIS Component Definitions

## Architecture Overview

JARVIS follows a **modular backend + React SPA frontend** architecture.

- **Backend**: Python FastAPI server — hosts all business logic, AI, voice, system, and data modules
- **Frontend**: React + TypeScript SPA — chat UI, voice waveform, system stats sidebar, notifications, calendar panel
- **Communication**: WebSocket (real-time bidirectional) + REST endpoints (commands, task CRUD)
- **Storage**: Local JSON files for conversation history and calendar/tasks
- **Config**: Central `config.py` / `config.json` for all tunable parameters

---

## Backend Components

### 1. IntentRouter
**Purpose**: Classifies incoming user messages and routes them to the appropriate handler module.

**Responsibilities**:
- Receive raw user message text
- Send message to Ollama with an intent-classification system prompt
- Parse the classified intent (chat, code, search, system, calendar, voice_control)
- Dispatch to the correct module handler
- Return a structured response envelope to the WebSocket layer

**Module**: `backend/intent_router.py`

---

### 2. AICore
**Purpose**: Manages all interactions with the local Ollama LLM (llama3.2:3b).

**Responsibilities**:
- Maintain and load/save conversation history from JSON
- Build context-aware prompts (include recent N messages as history)
- Send requests to the Ollama REST API (`/api/chat`)
- Apply module-specific system prompts (general chat vs coding vs intent classification)
- Return streamed or complete AI responses
- Handle Ollama unavailability gracefully

**Module**: `backend/ai_core.py`

---

### 3. VoiceModule
**Purpose**: Handles all voice I/O — speech-to-text input and text-to-speech output.

**Responsibilities**:
- Listen for microphone audio using `speech_recognition`
- Transcribe audio to text (Google STT or offline engine)
- Speak AI responses aloud using `pyttsx3`
- Manage voice mode state (active/inactive)
- Emit voice status events (listening_start, listening_end, speaking_start, speaking_end) over WebSocket
- Handle microphone unavailability gracefully (fall back to text mode)

**Module**: `backend/voice_module.py`

---

### 4. CodingAssistant
**Purpose**: Provides IDE-like coding assistance powered by Ollama.

**Responsibilities**:
- Detect coding-related intents (generate, explain, debug, refactor, review)
- Apply a coding-specific system prompt to Ollama requests
- Format code responses with language tags for syntax highlighting
- Return structured code response (language, code block, explanation)

**Module**: `backend/coding_assistant.py`

---

### 5. BrowserModule
**Purpose**: Performs web search and information retrieval using `browser-use`.

**Responsibilities**:
- Accept a search query or URL from the IntentRouter
- Execute web search via `browser-use` AI-native framework
- Extract and summarize relevant content from results
- Return a structured summary to the chat
- Handle browser-use failures gracefully

**Module**: `backend/browser_module.py`

---

### 6. SystemController
**Purpose**: Executes OS-level operations — file management, app launching, shell commands.

**Responsibilities**:
- Open URLs in the default browser
- Launch installed applications by name
- List, read, copy, move files/directories
- Delete files/directories (requires confirmation flag)
- Execute shell commands and capture output
- Enforce confirmation gate for destructive operations

**Module**: `backend/system_controller.py`

---

### 7. SystemMonitor
**Purpose**: Continuously monitors system health and emits stats and alerts over WebSocket.

**Responsibilities**:
- Poll CPU, RAM, and disk usage at configurable intervals (default 5s)
- Monitor running processes
- Monitor battery status (level, charging state) at configurable intervals (default 10s)
- Monitor network/Wi-Fi connectivity
- Emit real-time stats over WebSocket (multiplexed on main channel)
- Trigger alert events for: battery connected/disconnected, >90% charging, <30% discharging, Wi-Fi connected/disconnected, high CPU threshold
- Run as a background asyncio task

**Module**: `backend/system_monitor.py`

---

### 8. CalendarManager
**Purpose**: Manages local JSON-based calendar and task data.

**Responsibilities**:
- Load and save tasks from/to `data/tasks.json`
- Add a task (title, date, optional description, auto-generated ID)
- Remove a task by ID or title
- Query tasks: all, today, tomorrow, specific date
- Generate reminders for tasks due today and tomorrow
- Expose task data via REST endpoints (for dedicated UI panel)

**Module**: `backend/calendar_manager.py`

---

### 9. WebSocketManager
**Purpose**: Manages the WebSocket connection lifecycle and message multiplexing.

**Responsibilities**:
- Accept and maintain WebSocket connections from the React frontend
- Define message envelope format (`{ type, payload }`)
- Route incoming messages to IntentRouter
- Broadcast outgoing messages: chat responses, system stats, alerts, voice status, task updates
- Handle connection drops and reconnection

**Module**: `backend/websocket_manager.py`

---

### 10. ConfigManager
**Purpose**: Loads and provides access to all application configuration.

**Responsibilities**:
- Load `config.json` on startup
- Provide typed access to config values (model name, intervals, thresholds, ports)
- Support environment variable overrides

**Module**: `backend/config_manager.py`

---

## Frontend Components (React + TypeScript)

### 11. App (Root)
**Purpose**: Root component — sets up WebSocket connection, global state, and layout.

**Responsibilities**:
- Initialize and manage WebSocket connection
- Distribute incoming WebSocket messages to child components via context/state
- Render top-level layout (NotificationBar, ChatPanel, StatsSidebar)

**File**: `frontend/src/App.tsx`

---

### 12. ChatPanel
**Purpose**: Main chat interface — message history, input, voice toggle.

**Responsibilities**:
- Display conversation message history (user + JARVIS messages)
- Render code blocks with syntax highlighting (react-syntax-highlighter or similar)
- Provide text input field and send button
- Show voice waveform/indicator when voice is active
- Send user messages over WebSocket

**File**: `frontend/src/components/ChatPanel.tsx`

---

### 13. VoiceIndicator
**Purpose**: Visual feedback for voice input state.

**Responsibilities**:
- Display animated waveform when microphone is listening
- Display speaking indicator when TTS is active
- Show voice mode toggle button

**File**: `frontend/src/components/VoiceIndicator.tsx`

---

### 14. StatsSidebar
**Purpose**: Right sidebar displaying live system monitoring data.

**Responsibilities**:
- Display CPU, RAM, disk usage with progress bars or gauges
- Display battery level and charging status
- Display network/Wi-Fi status
- Update in real-time from WebSocket stats messages

**File**: `frontend/src/components/StatsSidebar.tsx`

---

### 15. NotificationBar
**Purpose**: Top bar for non-intrusive dismissible alert notifications.

**Responsibilities**:
- Display battery and network alert notifications
- Auto-dismiss after timeout or on user click
- Queue multiple alerts

**File**: `frontend/src/components/NotificationBar.tsx`

---

### 16. CalendarPanel
**Purpose**: Dedicated calendar/task management panel (accessible alongside chat).

**Responsibilities**:
- Display task list (all, today, tomorrow, by date)
- Provide UI to add/remove tasks
- Show reminders for today and tomorrow
- Communicate with backend via REST API endpoints

**File**: `frontend/src/components/CalendarPanel.tsx`

---

### 17. WebSocketContext
**Purpose**: React context providing WebSocket connection and message dispatch to all components.

**File**: `frontend/src/context/WebSocketContext.tsx`
