# JARVIS Application Design — Consolidated

## 1. Architecture Summary

JARVIS is a **modular AI personal assistant** with a clean separation between a Python FastAPI backend and a React + TypeScript frontend.

```
+─────────────────────────────────────────────────────────────+
|                    REACT + TYPESCRIPT FRONTEND               |
|                                                             |
|  +──────────────+  +──────────────+  +──────────────────+  |
|  | NotificationBar|  | StatsSidebar |  | CalendarPanel    |  |
|  +──────────────+  +──────────────+  +──────────────────+  |
|                                                             |
|  +─────────────────────────────────────────────────────+   |
|  |                    ChatPanel                         |   |
|  |  +──────────────────+  +────────────────────────+   |   |
|  |  | Message History  |  |   VoiceIndicator       |   |   |
|  |  +──────────────────+  +────────────────────────+   |   |
|  |  +────────────────────────────────────────────+     |   |
|  |  |           Text Input + Send Button         |     |   |
|  |  +────────────────────────────────────────────+     |   |
|  +─────────────────────────────────────────────────────+   |
|                                                             |
|  WebSocketContext (global WS connection + message dispatch) |
+─────────────────────────────────────────────────────────────+
                    |                    |
              WebSocket /ws         REST /api/*
                    |                    |
+─────────────────────────────────────────────────────────────+
|                    FASTAPI PYTHON BACKEND                    |
|                                                             |
|  +──────────────────────────────────────────────────────+  |
|  |                  JARVISService (main.py)              |  |
|  |  +──────────────+  +──────────────────────────────+  |  |
|  |  | WebSocket    |  |   REST Endpoints             |  |  |
|  |  | Manager      |  |   /api/tasks, /health        |  |  |
|  |  +──────────────+  +──────────────────────────────+  |  |
|  |                                                      |  |
|  |  +──────────────────────────────────────────────+   |  |
|  |  |              IntentRouter                    |   |  |
|  |  |  (LLM-based classification via Ollama)       |   |  |
|  |  +──────────────────────────────────────────────+   |  |
|  |         |        |        |        |        |        |  |
|  |         v        v        v        v        v        |  |
|  |  +──────+  +─────+  +────+  +─────+  +─────+        |  |
|  |  |AICore|  |Coding|  |Brow|  |Sys  |  |Cal  |        |  |
|  |  |      |  |Asst  |  |ser |  |Ctrl |  |Mgr  |        |  |
|  |  +──────+  +─────+  +────+  +─────+  +─────+        |  |
|  |                                                      |  |
|  |  +──────────────+  +──────────────────────────────+  |  |
|  |  | VoiceModule  |  |   SystemMonitor (background) |  |  |
|  |  | (STT + TTS)  |  |   (psutil polling loop)      |  |  |
|  |  +──────────────+  +──────────────────────────────+  |  |
|  |                                                      |  |
|  |  +──────────────────────────────────────────────+   |  |
|  |  |              ConfigManager                   |   |  |
|  |  +──────────────────────────────────────────────+   |  |
|  +──────────────────────────────────────────────────+  |  |
+─────────────────────────────────────────────────────────────+
                    |
+─────────────────────────────────────────────────────────────+
|                    LOCAL STORAGE (data/)                     |
|  conversation_history.json    tasks.json    config.json      |
+─────────────────────────────────────────────────────────────+
                    |
+─────────────────────────────────────────────────────────────+
|                    EXTERNAL SERVICES                         |
|  Ollama (localhost:11434)    browser-use (web)               |
+─────────────────────────────────────────────────────────────+
```

---

## 2. Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Real-time communication | WebSocket (multiplexed) | Single channel for chat, stats, alerts, voice status — simpler than multiple SSE streams |
| Intent routing | LLM-based (Ollama) | More flexible than keyword matching; handles natural language variations |
| Voice pipeline | Fully in Python backend | speech_recognition + pyttsx3 are Python libraries; frontend just shows status |
| System stats delivery | Multiplexed on main WebSocket | Avoids second connection; message type field differentiates data |
| Frontend layout | Single-page (chat center, stats sidebar, notifications top) | Clean, always-visible stats without tab switching |
| Calendar access | Chat + dedicated panel | Natural language via chat + structured view in panel |
| Storage | Local JSON files | Simple, no database dependency, fits single-user local app |
| Config | config.json + env var overrides | Tunable without code changes |

---

## 3. Component Summary

### Backend (Python)

| Component | Module | Role |
|---|---|---|
| ConfigManager | `config_manager.py` | Central config loading and access |
| AICore | `ai_core.py` | Ollama LLM integration + conversation history |
| IntentRouter | `intent_router.py` | LLM-based intent classification + dispatch |
| VoiceModule | `voice_module.py` | STT (speech_recognition) + TTS (pyttsx3) |
| CodingAssistant | `coding_assistant.py` | Code generation/explanation/debug/refactor/review |
| BrowserModule | `browser_module.py` | Web search + info retrieval (browser-use) |
| SystemController | `system_controller.py` | OS control: files, apps, shell commands |
| SystemMonitor | `system_monitor.py` | psutil polling + battery/network alerts |
| CalendarManager | `calendar_manager.py` | JSON-based task CRUD + reminders |
| WebSocketManager | `websocket_manager.py` | WS connection lifecycle + message routing |
| JARVISService | `main.py` | FastAPI app, startup/shutdown, orchestration |

### Frontend (React + TypeScript)

| Component | File | Role |
|---|---|---|
| App | `App.tsx` | Root layout, WS setup, global state |
| WebSocketContext | `context/WebSocketContext.tsx` | WS connection + message distribution |
| ChatPanel | `components/ChatPanel.tsx` | Chat UI, message history, input |
| VoiceIndicator | `components/VoiceIndicator.tsx` | Voice waveform + mode toggle |
| StatsSidebar | `components/StatsSidebar.tsx` | Live CPU/RAM/disk/battery/network display |
| NotificationBar | `components/NotificationBar.tsx` | Dismissible alert notifications |
| CalendarPanel | `components/CalendarPanel.tsx` | Task management UI + reminders |

---

## 4. Data Models

### conversation_history.json
```json
{
  "messages": [
    { "role": "user", "content": "...", "timestamp": "..." },
    { "role": "assistant", "content": "...", "timestamp": "..." }
  ]
}
```

### tasks.json
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "...",
      "date": "YYYY-MM-DD",
      "description": "...",
      "created_at": "ISO 8601"
    }
  ]
}
```

### config.json
```json
{
  "ollama_model": "llama3.2:3b",
  "ollama_base_url": "http://localhost:11434",
  "stats_interval_seconds": 5,
  "battery_interval_seconds": 10,
  "cpu_alert_threshold": 90.0,
  "history_context_window": 20,
  "backend_port": 8000,
  "data_dir": "./data"
}
```

---

## 5. Project Directory Structure (Preview)

```
jarvis/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config_manager.py
│   ├── ai_core.py
│   ├── intent_router.py
│   ├── voice_module.py
│   ├── coding_assistant.py
│   ├── browser_module.py
│   ├── system_controller.py
│   ├── system_monitor.py
│   ├── calendar_manager.py
│   └── websocket_manager.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── context/
│   │   │   └── WebSocketContext.tsx
│   │   └── components/
│   │       ├── ChatPanel.tsx
│   │       ├── VoiceIndicator.tsx
│   │       ├── StatsSidebar.tsx
│   │       ├── NotificationBar.tsx
│   │       └── CalendarPanel.tsx
│   ├── package.json
│   └── tsconfig.json
├── data/
│   ├── conversation_history.json
│   └── tasks.json
├── config.json
├── requirements.txt
└── README.md
```

---

## 6. References

- Component definitions: `components.md`
- Method signatures: `component-methods.md`
- Service layer: `services.md`
- Dependency map: `component-dependency.md`
