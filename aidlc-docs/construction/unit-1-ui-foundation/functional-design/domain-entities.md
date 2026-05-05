# Unit 1: UI Foundation — Domain Entities

## Core Entities

### WSMessage
Represents a message exchanged over the WebSocket channel.

```
WSMessage
├── type: string          — message category (e.g. "chat_response", "stats_update", "alert")
├── payload: object       — type-specific data
└── timestamp: string     — ISO 8601 datetime
```

### AppConfig
Represents the application configuration loaded from config.json.

```
AppConfig
├── ollama_model: string           — LLM model name (default: "llama3.2:3b")
├── ollama_base_url: string        — Ollama API base URL (default: "http://localhost:11434")
├── stats_interval_seconds: int    — monitoring refresh interval (default: 5)
├── battery_interval_seconds: int  — battery/network poll interval (default: 10)
├── cpu_alert_threshold: float     — CPU alert trigger % (default: 90.0)
├── history_context_window: int    — conversation history window (default: 20)
├── backend_port: int              — FastAPI server port (default: 8000)
└── data_dir: string               — path to data directory (default: "./data")
```

### ConnectionState (Frontend)
Represents the WebSocket connection state in the React app.

```
ConnectionState
├── socket: WebSocket | null       — active WebSocket instance
├── connected: boolean             — connection status
└── lastMessage: WSMessage | null  — most recently received message
```

### UILayout
Represents the single-page layout structure.

```
UILayout
├── NotificationBar (top)          — alert notifications strip
├── MainContent
│   ├── ChatPanel (center)         — primary chat interface
│   └── StatsSidebar (right)       — system stats panel
└── CalendarPanel (accessible)     — task management panel (toggle/overlay)
```
