# Unit 1: UI Foundation — Business Logic Model

## Overview

Unit 1 establishes the application skeleton with no AI or module logic. The core business logic in this unit is:
1. Configuration loading and validation
2. WebSocket connection lifecycle management
3. Message envelope routing (receive → identify type → dispatch to handler)
4. Frontend state management and layout rendering

---

## 1. Configuration Loading Logic

```
START
  Load config.json from working directory
  IF file not found:
    Use all default values
    Log warning: "config.json not found, using defaults"
  FOR each config key:
    Check for matching environment variable (e.g. JARVIS_OLLAMA_MODEL)
    IF env var exists: override config value with env var
  Validate types (int, float, string)
  IF validation fails: log error and use default for that key
  Create data/ directory if not exists
  Create data/conversation_history.json if not exists → { "messages": [] }
  Create data/tasks.json if not exists → { "tasks": [] }
END
```

---

## 2. WebSocket Connection Lifecycle

### Backend (FastAPI)
```
ON WebSocket connect request at /ws:
  Accept connection
  Store in WebSocketManager.active_connection
  IF previous connection exists: close it (single-user)
  Log: "WebSocket client connected"

ON message received:
  Parse JSON → WSMessage envelope
  Extract type and payload
  Dispatch to registered handler for type
  IF no handler: log warning, send error response

ON WebSocket disconnect:
  Remove from active_connection
  Log: "WebSocket client disconnected"
  Do NOT crash — await next connection
```

### Frontend (React)
```
ON App mount:
  Create WebSocket(ws://localhost:8000/ws)
  Set connected = false

ON WebSocket open:
  Set connected = true
  Update connection indicator → "Connected"

ON WebSocket message:
  Parse JSON → WSMessage
  Store as lastMessage in context
  Dispatch to component handlers via context

ON WebSocket close / error:
  Set connected = false
  Update connection indicator → "Disconnected"
  Schedule reconnect attempt after 3 seconds
  Retry up to 5 times with exponential backoff
```

---

## 3. Message Routing Logic (Unit 1 — Echo Mode)

In Unit 1, the backend has no AI or module handlers yet. All incoming `user_message` types are echoed back as a `chat_response` to verify end-to-end connectivity.

```
ON receive WSMessage(type="user_message", payload={ text }):
  Create response = WSMessage(
    type = "chat_response",
    payload = { text: "[Echo] " + payload.text, message_type: "text" },
    timestamp = now()
  )
  Send response to client

ON receive WSMessage(type="voice_toggle"):
  Acknowledge with WSMessage(type="voice_status", payload={ status: "toggled" })

ON receive any other type:
  Log: "Unhandled message type: {type}"
  Send WSMessage(type="error", payload={ message: "Unknown message type", code: "UNKNOWN_TYPE" })
```

---

## 4. Frontend State Management

### Global State (App.tsx + WebSocketContext)
```
State:
  socket: WebSocket | null
  connected: boolean
  lastMessage: WSMessage | null
  notifications: Notification[]
  systemStats: SystemStats | null
  calendarOpen: boolean

Derived actions:
  sendMessage(type, payload) → socket.send(JSON.stringify({ type, payload, timestamp }))
  dismissNotification(id) → filter notifications by id
  toggleCalendar() → toggle calendarOpen boolean
```

### ChatPanel State (local)
```
State:
  messages: Message[]       — conversation display list
  inputText: string         — current text input value
  sending: boolean          — request in flight

On send:
  IF inputText.trim() is empty: do nothing
  Append { role: "user", content: inputText } to messages
  sendMessage("user_message", { text: inputText })
  Clear inputText
  Set sending = true

On chat_response received:
  Append { role: "assistant", content: payload.text } to messages
  Set sending = false
```

---

## 5. Layout Rendering Logic

```
App renders:
  <NotificationBar notifications={notifications} onDismiss={dismissNotification} />
  <div className="main-layout">
    <ChatPanel />                          // center, flex-grow
    <StatsSidebar stats={systemStats} />   // right, fixed width
  </div>
  {calendarOpen && <CalendarPanel />}      // overlay/panel when open
  <button onClick={toggleCalendar}>        // calendar toggle button
```

Placeholder rendering rules (Unit 1):
- StatsSidebar with null stats → show skeleton/loading state
- NotificationBar with empty array → render nothing (zero height)
- CalendarPanel → show "Calendar coming soon" placeholder
- VoiceIndicator → show disabled microphone icon
