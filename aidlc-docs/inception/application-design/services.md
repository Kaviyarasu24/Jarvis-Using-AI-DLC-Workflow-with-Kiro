# JARVIS Services

## Service Layer Overview

The service layer in JARVIS is implemented as a **FastAPI application** that orchestrates all backend components. There is one primary orchestration service (`JARVISService`) and supporting async background services.

---

## 1. JARVISService (Main Orchestrator)

**Purpose**: Central orchestrator that wires all modules together and handles the request/response lifecycle.

**Responsibilities**:
- Initialize all modules on startup (AICore, VoiceModule, SystemMonitor, CalendarManager, etc.)
- Register the WebSocket endpoint and delegate to WebSocketManager
- Register REST endpoints for calendar CRUD and health check
- Route incoming WebSocket messages through IntentRouter
- Coordinate confirmation flow for destructive system operations
- Shut down all modules cleanly on application exit

**Startup sequence**:
1. Load ConfigManager
2. Initialize AICore → load conversation history
3. Initialize CalendarManager → load tasks
4. Initialize WebSocketManager
5. Initialize VoiceModule (check mic availability)
6. Initialize SystemMonitor → start background monitoring loop
7. Initialize IntentRouter with all module handlers
8. Start FastAPI server

**File**: `backend/main.py`

---

## 2. IntentDispatchService

**Purpose**: Encapsulates the full intent classification → dispatch → response pipeline.

**Flow**:
```
User Message (WebSocket)
        |
        v
  IntentRouter.classify_intent()   [Ollama LLM call]
        |
        v
  Route to handler:
    "chat"          --> AICore.chat()
    "code"          --> CodingAssistant.handle()
    "search"        --> BrowserModule.search()
    "system"        --> SystemController (action parsing)
    "calendar"      --> CalendarManager (action parsing)
    "voice_control" --> VoiceModule.set_voice_mode()
        |
        v
  Wrap result in WSMessage envelope
        |
        v
  WebSocketManager.send()  [back to frontend]
```

**Confirmation sub-flow** (for destructive system operations):
```
SystemController returns ActionResult(requires_confirmation=True)
        |
        v
JARVISService sends WSMessage(type="confirmation_required", payload={action, details})
        |
        v
Frontend displays confirmation dialog
        |
        v
User confirms → WebSocket message(type="confirm_action", payload={action_id})
        |
        v
JARVISService re-invokes SystemController with confirmed=True
```

---

## 3. MonitoringService (Background)

**Purpose**: Runs as a persistent asyncio background task, continuously polling system metrics and pushing updates to all connected WebSocket clients.

**Responsibilities**:
- Poll system stats every `stats_interval_seconds` (default 5s)
- Poll battery + network every `battery_interval_seconds` (default 10s)
- Emit `WSMessage(type="stats_update", payload=SystemStats)` to all clients
- Emit `WSMessage(type="alert", payload=Alert)` when alert conditions are triggered
- Maintain previous state to detect transitions (e.g., charger plugged in = state change from not-charging to charging)

**Lifecycle**: Started on FastAPI `startup` event, cancelled on `shutdown` event.

---

## 4. VoiceOrchestrationService

**Purpose**: Manages the voice interaction loop when voice mode is active.

**Flow** (voice mode active):
```
VoiceModule.start_listening()
        |
        v
Transcribed text
        |
        v
IntentDispatchService (same as text input)
        |
        v
AI response text
        |
        v
VoiceModule.speak(response_text)
```

**WebSocket events emitted during voice flow**:
- `voice_status: "listening_start"` — mic activated
- `voice_status: "listening_end"` — transcription complete
- `voice_status: "speaking_start"` — TTS started
- `voice_status: "speaking_end"` — TTS finished

---

## 5. REST API Endpoints (FastAPI)

These endpoints support the React CalendarPanel and health monitoring:

| Method | Path | Handler | Description |
|---|---|---|---|
| `GET` | `/health` | JARVISService | Health check — Ollama reachability, mic status |
| `GET` | `/api/tasks` | CalendarManager | Get all tasks |
| `GET` | `/api/tasks/today` | CalendarManager | Get today's tasks |
| `GET` | `/api/tasks/tomorrow` | CalendarManager | Get tomorrow's tasks |
| `GET` | `/api/tasks/date/{date}` | CalendarManager | Get tasks for specific date |
| `POST` | `/api/tasks` | CalendarManager | Add a new task |
| `DELETE` | `/api/tasks/{task_id}` | CalendarManager | Remove task by ID |
| `GET` | `/api/reminders` | CalendarManager | Get today + tomorrow reminders |
| `WebSocket` | `/ws` | WebSocketManager | Main bidirectional channel |

---

## 6. WebSocket Message Type Registry

All message types flowing over the `/ws` WebSocket channel:

### Frontend → Backend
| type | payload | Description |
|---|---|---|
| `user_message` | `{ text: string }` | User chat/command input |
| `voice_toggle` | `{ enabled: boolean }` | Enable/disable voice mode |
| `confirm_action` | `{ action_id: string }` | Confirm a destructive operation |
| `clear_history` | `{}` | Clear conversation history |

### Backend → Frontend
| type | payload | Description |
|---|---|---|
| `chat_response` | `{ text, message_type, language? }` | AI response (text or code) |
| `stats_update` | `SystemStats` | Live system monitoring data |
| `alert` | `Alert` | Battery/network/system alert |
| `voice_status` | `{ status: string }` | Voice pipeline state change |
| `confirmation_required` | `{ action_id, action, details }` | Destructive op needs confirmation |
| `error` | `{ message, code }` | Error notification |
| `task_update` | `{ tasks: Task[] }` | Calendar task list update |
