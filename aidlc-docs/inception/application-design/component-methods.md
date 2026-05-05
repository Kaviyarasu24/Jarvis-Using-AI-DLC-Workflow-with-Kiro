# JARVIS Component Methods

> Note: Detailed business rules and logic are defined in Functional Design (Construction phase, per unit).
> This document covers method signatures, purposes, and input/output contracts.

---

## WebSocket Message Envelope

All WebSocket messages use this envelope:

```typescript
// Frontend (TypeScript)
interface WSMessage {
  type: string;       // e.g. "chat_response", "stats_update", "alert", "voice_status"
  payload: unknown;   // type-specific payload
  timestamp: string;  // ISO 8601
}
```

```python
# Backend (Python)
@dataclass
class WSMessage:
    type: str
    payload: dict
    timestamp: str  # ISO 8601
```

---

## Backend Method Signatures

### IntentRouter

```python
class IntentRouter:
    def __init__(self, ai_core: AICore, handlers: dict[str, Callable])
    
    async def route(self, message: str, session_id: str) -> WSMessage
    # Classifies intent via Ollama, dispatches to handler, returns response envelope
    
    async def classify_intent(self, message: str) -> str
    # Returns intent label: "chat" | "code" | "search" | "system" | "calendar" | "voice_control"
```

---

### AICore

```python
class AICore:
    def __init__(self, config: ConfigManager)
    
    async def chat(self, message: str, system_prompt: str | None = None) -> str
    # Sends message + history to Ollama /api/chat, returns response text
    
    async def chat_stream(self, message: str, system_prompt: str | None = None) -> AsyncGenerator[str, None]
    # Streams response tokens from Ollama
    
    def load_history(self) -> list[dict]
    # Loads conversation history from data/conversation_history.json
    
    def save_history(self) -> None
    # Persists current history to data/conversation_history.json
    
    def append_to_history(self, role: str, content: str) -> None
    # Appends a message to in-memory history (role: "user" | "assistant")
    
    def get_context_window(self, n: int) -> list[dict]
    # Returns last N messages for context injection
    
    def clear_history(self) -> None
    # Clears in-memory and persisted history
    
    async def health_check(self) -> bool
    # Returns True if Ollama API is reachable
```

---

### VoiceModule

```python
class VoiceModule:
    def __init__(self, config: ConfigManager, ws_manager: WebSocketManager)
    
    async def start_listening(self) -> str
    # Activates microphone, captures audio, returns transcribed text
    # Emits voice_status: "listening_start" / "listening_end" over WebSocket
    
    async def speak(self, text: str) -> None
    # Converts text to speech via pyttsx3
    # Emits voice_status: "speaking_start" / "speaking_end" over WebSocket
    
    def set_voice_mode(self, enabled: bool) -> None
    # Enables or disables voice mode
    
    def is_available(self) -> bool
    # Returns True if microphone is accessible
    
    def get_status(self) -> dict
    # Returns { "mode": "voice"|"text", "listening": bool, "speaking": bool }
```

---

### CodingAssistant

```python
class CodingAssistant:
    def __init__(self, ai_core: AICore)
    
    async def handle(self, message: str) -> CodingResponse
    # Detects coding task type, applies system prompt, returns structured response
    
    def detect_task_type(self, message: str) -> str
    # Returns: "generate" | "explain" | "debug" | "refactor" | "review"
    
    async def generate_code(self, description: str, language: str | None) -> CodingResponse
    async def explain_code(self, code: str) -> CodingResponse
    async def debug_code(self, code: str, error: str | None) -> CodingResponse
    async def refactor_code(self, code: str, instructions: str) -> CodingResponse
    async def review_code(self, code: str) -> CodingResponse

@dataclass
class CodingResponse:
    language: str        # detected/specified programming language
    code: str | None     # code block (if applicable)
    explanation: str     # human-readable explanation
    task_type: str       # generate | explain | debug | refactor | review
```

---

### BrowserModule

```python
class BrowserModule:
    def __init__(self, config: ConfigManager)
    
    async def search(self, query: str) -> BrowserResult
    # Executes web search via browser-use, returns summarized result
    
    async def fetch_url(self, url: str) -> BrowserResult
    # Fetches and summarizes content from a specific URL

@dataclass
class BrowserResult:
    success: bool
    query: str
    summary: str          # AI-summarized content
    sources: list[str]    # source URLs
    error: str | None
```

---

### SystemController

```python
class SystemController:
    def __init__(self, config: ConfigManager)
    
    async def open_url(self, url: str) -> ActionResult
    # Opens URL in default browser
    
    async def launch_app(self, app_name: str) -> ActionResult
    # Launches application by name
    
    async def list_directory(self, path: str) -> ActionResult
    # Lists files/directories at path
    
    async def read_file(self, path: str) -> ActionResult
    # Reads file content
    
    async def copy_file(self, src: str, dst: str) -> ActionResult
    # Copies file/directory
    
    async def move_file(self, src: str, dst: str) -> ActionResult
    # Moves file/directory
    
    async def delete_file(self, path: str, confirmed: bool = False) -> ActionResult
    # Deletes file/directory — requires confirmed=True
    
    async def run_command(self, command: str, confirmed: bool = False) -> ActionResult
    # Executes shell command — requires confirmed=True

@dataclass
class ActionResult:
    success: bool
    output: str | None
    requires_confirmation: bool   # True if destructive and not yet confirmed
    error: str | None
```

---

### SystemMonitor

```python
class SystemMonitor:
    def __init__(self, config: ConfigManager, ws_manager: WebSocketManager)
    
    async def start(self) -> None
    # Starts background monitoring loop (asyncio task)
    
    async def stop(self) -> None
    # Stops monitoring loop
    
    async def get_stats(self) -> SystemStats
    # Returns current snapshot of system stats
    
    async def _monitor_loop(self) -> None
    # Internal: polls stats, checks thresholds, emits WebSocket events
    
    def _check_battery_alerts(self, battery: BatteryInfo, prev: BatteryInfo) -> list[Alert]
    # Returns list of triggered battery alerts
    
    def _check_network_alerts(self, connected: bool, prev_connected: bool) -> list[Alert]
    # Returns list of triggered network alerts

@dataclass
class SystemStats:
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    battery_level: float | None
    battery_charging: bool | None
    network_connected: bool
    processes: list[dict]
    timestamp: str

@dataclass
class Alert:
    type: str       # "battery_connected" | "battery_disconnected" | "battery_high" | "battery_low" | "wifi_connected" | "wifi_disconnected" | "cpu_high"
    message: str
    severity: str   # "info" | "warning" | "critical"
    timestamp: str
```

---

### CalendarManager

```python
class CalendarManager:
    def __init__(self, config: ConfigManager)
    
    def load_tasks(self) -> list[Task]
    # Loads tasks from data/tasks.json
    
    def save_tasks(self) -> None
    # Persists tasks to data/tasks.json
    
    def add_task(self, title: str, date: str, description: str = "") -> Task
    # Creates task with auto-generated ID, saves immediately
    
    def remove_task(self, task_id: str | None = None, title: str | None = None) -> bool
    # Removes task by ID or title match, returns success
    
    def get_all_tasks(self) -> list[Task]
    def get_tasks_for_date(self, date: str) -> list[Task]   # date: "YYYY-MM-DD"
    def get_today_tasks(self) -> list[Task]
    def get_tomorrow_tasks(self) -> list[Task]
    
    def get_reminders(self) -> list[Task]
    # Returns tasks due today and tomorrow

@dataclass
class Task:
    id: str           # UUID
    title: str
    date: str         # "YYYY-MM-DD"
    description: str
    created_at: str   # ISO 8601
```

---

### WebSocketManager

```python
class WebSocketManager:
    def __init__(self)
    
    async def connect(self, websocket: WebSocket) -> None
    # Accepts and registers a WebSocket connection
    
    async def disconnect(self, websocket: WebSocket) -> None
    # Removes a WebSocket connection
    
    async def send(self, websocket: WebSocket, message: WSMessage) -> None
    # Sends a message to a specific connection
    
    async def broadcast(self, message: WSMessage) -> None
    # Sends a message to all active connections
    
    async def receive(self, websocket: WebSocket) -> dict
    # Receives and parses an incoming WebSocket message
```

---

### ConfigManager

```python
class ConfigManager:
    def __init__(self, config_path: str = "config.json")
    
    def load(self) -> None
    # Loads config from file, applies env var overrides
    
    @property
    def ollama_model(self) -> str          # default: "llama3.2:3b"
    
    @property
    def ollama_base_url(self) -> str       # default: "http://localhost:11434"
    
    @property
    def stats_interval_seconds(self) -> int   # default: 5
    
    @property
    def battery_interval_seconds(self) -> int # default: 10
    
    @property
    def cpu_alert_threshold(self) -> float    # default: 90.0
    
    @property
    def history_context_window(self) -> int   # default: 20 (last N messages)
    
    @property
    def backend_port(self) -> int             # default: 8000
    
    @property
    def data_dir(self) -> str                 # default: "./data"
```

---

## Frontend Method Signatures (React + TypeScript)

### WebSocketContext

```typescript
interface WebSocketContextValue {
  socket: WebSocket | null;
  connected: boolean;
  sendMessage: (type: string, payload: unknown) => void;
  lastMessage: WSMessage | null;
}

// Hook
function useWebSocket(): WebSocketContextValue
```

---

### ChatPanel

```typescript
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  type: "text" | "code";
  language?: string;
  timestamp: string;
}

interface ChatPanelProps {}

// Internal handlers
function handleSend(text: string): void       // sends chat message over WebSocket
function handleVoiceToggle(): void            // toggles voice mode via WebSocket
function handleIncomingMessage(msg: WSMessage): void  // processes chat_response messages
```

---

### StatsSidebar

```typescript
interface SystemStats {
  cpu_percent: number;
  ram_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  disk_percent: number;
  battery_level: number | null;
  battery_charging: boolean | null;
  network_connected: boolean;
}

interface StatsSidebarProps {
  stats: SystemStats | null;
}
```

---

### NotificationBar

```typescript
interface Notification {
  id: string;
  type: string;
  message: string;
  severity: "info" | "warning" | "critical";
  timestamp: string;
}

interface NotificationBarProps {
  notifications: Notification[];
  onDismiss: (id: string) => void;
}
```

---

### CalendarPanel

```typescript
interface Task {
  id: string;
  title: string;
  date: string;
  description: string;
  created_at: string;
}

interface CalendarPanelProps {}

// Internal handlers
function handleAddTask(title: string, date: string, description?: string): Promise<void>
function handleRemoveTask(id: string): Promise<void>
function handleViewTasks(filter: "all" | "today" | "tomorrow" | string): Promise<void>
```
