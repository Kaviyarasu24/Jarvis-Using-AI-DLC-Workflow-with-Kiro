# Unit 1: UI Foundation — Logical Components

## Backend Logical Components

### ConfigManager (Singleton)
- Loaded once at startup, shared across all modules via dependency injection
- Immutable after load — no runtime config changes
- Provides typed property accessors (no raw dict access in other modules)

### WebSocketManager (Connection Registry)
- Holds reference to the single active WebSocket connection
- Provides `send()` and `broadcast()` methods used by all backend modules
- Handles connection/disconnection events cleanly

### FastAPI Application Instance
- Single `app = FastAPI()` instance in `main.py`
- All routes registered on this instance
- Lifespan context manager handles startup/shutdown hooks

### Data Directory Initializer
- Runs once at startup before any module accesses data files
- Creates `data/` directory if missing
- Creates `conversation_history.json` and `tasks.json` with empty structures if missing

## Frontend Logical Components

### WebSocket Connection Manager (inside App.tsx)
- Single WebSocket instance per app session
- Reconnection scheduler with exponential backoff
- Message parser and dispatcher

### Global State Store (WebSocketContext)
- Holds: connection status, last message, notifications list, system stats
- Provides: `sendMessage()`, `dismissNotification()`
- All components subscribe via `useWebSocket()` hook

### Message Renderer (inside ChatPanel)
- Renders `Message[]` list
- Differentiates user vs assistant vs error messages
- Auto-scroll management
- In Unit 1: plain text only (code rendering added in Unit 6)

### Layout Shell
- CSS Grid/Flexbox layout
- Responsive breakpoints
- Calendar panel toggle state

## Infrastructure (Local Only)

| Component | Type | Purpose |
|---|---|---|
| `data/` directory | Local filesystem | Persistent JSON storage |
| `config.json` | Local file | Application configuration |
| Uvicorn | Process | ASGI server for FastAPI |
| Vite dev server | Process (dev only) | React HMR + WS proxy |

No external services, no databases, no cloud resources in Unit 1.
