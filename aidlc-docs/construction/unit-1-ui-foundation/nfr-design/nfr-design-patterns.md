# Unit 1: UI Foundation — NFR Design Patterns

## 1. Resilience Patterns

### Backend: Graceful Degradation on Bad Input
```python
# WebSocket message handler — never crash on bad input
async def handle_message(data: str) -> WSMessage | None:
    try:
        msg = json.loads(data)
        return WSMessage(**msg)
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning(f"Malformed WebSocket message: {e}")
        return WSMessage(type="error", payload={"message": "Invalid message format"}, timestamp=now())
```

### Frontend: Exponential Backoff Reconnection
```typescript
// Reconnect with increasing delays: 1s, 2s, 4s, 8s, 16s
const BACKOFF_DELAYS = [1000, 2000, 4000, 8000, 16000]

function scheduleReconnect(attempt: number) {
  const delay = BACKOFF_DELAYS[Math.min(attempt, BACKOFF_DELAYS.length - 1)]
  setTimeout(() => connectWebSocket(), delay)
}
```

### Config: Fallback to Defaults
```python
# ConfigManager — never fail on missing keys
def _get(self, key: str, default: Any) -> Any:
    try:
        return self._config.get(key, default)
    except Exception:
        return default
```

## 2. Performance Patterns

### Frontend: Message Batching Prevention
React 18 automatic batching handles multiple state updates from a single WebSocket message in one render cycle — no manual batching needed.

### Frontend: Scroll Optimization
```typescript
// Use useRef + scrollIntoView instead of scrollTop manipulation
// Only scroll if user is near the bottom (don't interrupt manual scroll-up)
const isNearBottom = () => {
  const el = messagesEndRef.current?.parentElement
  if (!el) return true
  return el.scrollHeight - el.scrollTop - el.clientHeight < 100
}
useEffect(() => {
  if (isNearBottom()) messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages])
```

### Backend: Async-First
All FastAPI route handlers and WebSocket handlers are `async def` — no blocking I/O on the event loop.

## 3. Maintainability Patterns

### Single Source of Truth for Types
All shared types defined once in `frontend/src/types/index.ts` and imported everywhere. Backend dataclasses mirror frontend interfaces.

### Context Isolation
WebSocket logic is fully encapsulated in `WebSocketContext`. Components only call `sendMessage()` and read `lastMessage` — they never touch the raw WebSocket object.

### Module Boundary Enforcement
```python
# main.py is the ONLY file that imports and wires modules together
# Each module only imports ConfigManager and its direct dependencies
# No module imports from main.py (no circular deps)
```

## 4. Security Patterns

### CORS Lockdown
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

### No Secrets in Frontend
- Backend URL is the only config the frontend needs: `ws://localhost:8000/ws`
- Hardcoded to localhost — no external endpoints, no API keys in frontend code
