# JARVIS Component Dependency Map

## Dependency Matrix

| Component | Depends On | Used By |
|---|---|---|
| ConfigManager | — | All components |
| AICore | ConfigManager | IntentRouter, CodingAssistant |
| VoiceModule | ConfigManager, WebSocketManager | JARVISService (VoiceOrchestrationService) |
| CodingAssistant | AICore | IntentRouter |
| BrowserModule | ConfigManager | IntentRouter |
| SystemController | ConfigManager | IntentRouter |
| SystemMonitor | ConfigManager, WebSocketManager | JARVISService (MonitoringService) |
| CalendarManager | ConfigManager | IntentRouter, REST endpoints |
| IntentRouter | AICore, CodingAssistant, BrowserModule, SystemController, CalendarManager, VoiceModule | JARVISService |
| WebSocketManager | — | IntentRouter, SystemMonitor, VoiceModule, JARVISService |
| JARVISService (main.py) | All backend components | — (entry point) |

---

## Frontend Dependency Map

| Component | Depends On | Used By |
|---|---|---|
| WebSocketContext | — | App, ChatPanel, StatsSidebar, NotificationBar |
| App | WebSocketContext, ChatPanel, StatsSidebar, NotificationBar, CalendarPanel | — (root) |
| ChatPanel | WebSocketContext, VoiceIndicator | App |
| VoiceIndicator | WebSocketContext | ChatPanel |
| StatsSidebar | WebSocketContext | App |
| NotificationBar | WebSocketContext | App |
| CalendarPanel | REST API (fetch) | App |

---

## Communication Patterns

### Backend Internal Communication
```
ConfigManager  <──────────────────────────────────────────────
                                                              |
User Input (WebSocket)                                        |
      |                                                       |
      v                                                       |
WebSocketManager                                              |
      |                                                       |
      v                                                       |
IntentRouter ──[classify via Ollama]──> AICore               |
      |                                                       |
      +──[intent: chat]──────────────> AICore ───────────────+
      |                                                       |
      +──[intent: code]──────────────> CodingAssistant ──────+
      |                                                       |
      +──[intent: search]────────────> BrowserModule ─────────+
      |                                                       |
      +──[intent: system]────────────> SystemController ──────+
      |                                                       |
      +──[intent: calendar]──────────> CalendarManager ───────+
      |                                                       |
      +──[intent: voice_control]─────> VoiceModule ───────────+
      |
      v
WebSocketManager ──> Frontend (WSMessage response)

Background Tasks (independent of user input):
SystemMonitor ──[every 5s]──> WebSocketManager ──> Frontend (stats_update)
SystemMonitor ──[on event]──> WebSocketManager ──> Frontend (alert)
VoiceModule   ──[on state]──> WebSocketManager ──> Frontend (voice_status)
```

### Frontend ↔ Backend Communication
```
React App
  |
  +── WebSocket /ws ──────────────────────────────> FastAPI WebSocketManager
  |     (bidirectional, multiplexed)                      |
  |     user_message, voice_toggle,                       |
  |     confirm_action, clear_history                     |
  |                                                       |
  |     <── chat_response, stats_update,                  |
  |         alert, voice_status,                          |
  |         confirmation_required, error,                 |
  |         task_update                                   |
  |
  +── REST /api/tasks* ───────────────────────────> FastAPI REST endpoints
        (CalendarPanel CRUD)                              |
        GET /api/tasks                                    |
        POST /api/tasks                                   |
        DELETE /api/tasks/{id}                            |
        GET /api/reminders                                |
```

---

## Data Flow Diagrams

### Chat Message Flow
```
[User types/speaks]
      |
      v
[ChatPanel] --WS--> [WebSocketManager] --> [IntentRouter]
                                                  |
                                          [classify_intent via Ollama]
                                                  |
                                          [route to handler]
                                                  |
                                          [handler returns result]
                                                  |
                                    [WebSocketManager.send(chat_response)]
                                                  |
[ChatPanel displays response] <--WS--------------+
[VoiceModule.speak()] (if voice mode on)
```

### System Monitoring Flow
```
[SystemMonitor background task]
      |
      +--[every 5s]--> [psutil.cpu/ram/disk] --> [SystemStats]
      |                                                |
      +--[every 10s]--> [psutil.battery/net] --> [SystemStats + Alert check]
                                                       |
                                          [WebSocketManager.broadcast(stats_update)]
                                                       |
                              [StatsSidebar updates] <-+
                              [NotificationBar shows alert] (if alert triggered)
```

### Voice Interaction Flow
```
[User clicks voice toggle]
      |
      v
[ChatPanel] --WS(voice_toggle)--> [WebSocketManager] --> [VoiceModule.set_voice_mode(true)]
                                                                |
                                                    [VoiceModule.start_listening()]
                                                                |
                                              [WS: voice_status "listening_start"]
                                                                |
                                                    [speech_recognition captures audio]
                                                                |
                                              [WS: voice_status "listening_end"]
                                                                |
                                                    [transcribed text --> IntentRouter]
                                                                |
                                                    [AI response text]
                                                                |
                                              [WS: chat_response to ChatPanel]
                                                                |
                                                    [VoiceModule.speak(response)]
                                                                |
                                              [WS: voice_status "speaking_start/end"]
```

---

## Module Isolation Boundaries

Each backend module is independently importable and testable:

| Module | External Dependencies | Mockable For Testing |
|---|---|---|
| ConfigManager | File system | Yes (in-memory config) |
| AICore | Ollama HTTP API | Yes (mock HTTP client) |
| VoiceModule | Microphone hardware, pyttsx3 | Yes (mock audio I/O) |
| CodingAssistant | AICore | Yes (mock AICore) |
| BrowserModule | browser-use, network | Yes (mock browser-use) |
| SystemController | OS / file system | Yes (mock subprocess/os) |
| SystemMonitor | psutil, WebSocketManager | Yes (mock psutil) |
| CalendarManager | File system | Yes (in-memory store) |
| WebSocketManager | FastAPI WebSocket | Yes (mock WebSocket) |
