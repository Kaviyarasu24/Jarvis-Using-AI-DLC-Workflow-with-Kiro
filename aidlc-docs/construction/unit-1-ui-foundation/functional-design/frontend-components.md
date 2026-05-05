# Unit 1: UI Foundation — Frontend Components

## Component Hierarchy

```
App
├── WebSocketContext.Provider
│   ├── NotificationBar
│   ├── div.main-layout
│   │   ├── ChatPanel
│   │   │   ├── div.messages-list
│   │   │   │   └── MessageBubble (per message)
│   │   │   ├── VoiceIndicator (placeholder)
│   │   │   └── div.input-area
│   │   │       ├── textarea.chat-input
│   │   │       └── button.send-btn
│   │   └── StatsSidebar (placeholder)
│   └── CalendarPanel (placeholder, conditional)
└── button.calendar-toggle
```

---

## Component Specifications

### App (`App.tsx`)

**Props**: none

**State**:
```typescript
const [connected, setConnected] = useState(false)
const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)
const [notifications, setNotifications] = useState<Notification[]>([])
const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
const [calendarOpen, setCalendarOpen] = useState(false)
const socketRef = useRef<WebSocket | null>(null)
```

**Behavior**:
- On mount: create WebSocket, set up event handlers, store in ref
- On unmount: close WebSocket
- On message: parse WSMessage, dispatch to state setters by type
- Provide all state + `sendMessage` via WebSocketContext

**Reconnection logic**:
```typescript
const reconnectAttempts = useRef(0)
const MAX_RECONNECTS = 5
const RECONNECT_DELAY_MS = [1000, 2000, 4000, 8000, 16000]
```

---

### WebSocketContext (`context/WebSocketContext.tsx`)

**Context value type**:
```typescript
interface WebSocketContextValue {
  connected: boolean
  sendMessage: (type: string, payload: unknown) => void
  lastMessage: WSMessage | null
  notifications: Notification[]
  systemStats: SystemStats | null
  dismissNotification: (id: string) => void
}
```

**Hook**: `export function useWebSocket(): WebSocketContextValue`

---

### ChatPanel (`components/ChatPanel.tsx`)

**Props**: none (reads from WebSocketContext)

**State**:
```typescript
const [messages, setMessages] = useState<Message[]>([])
const [inputText, setInputText] = useState('')
const [sending, setSending] = useState(false)
const messagesEndRef = useRef<HTMLDivElement>(null)
```

**User interactions**:
- Type in textarea → updates `inputText`
- Press Enter (without Shift) or click Send → calls `handleSend()`
- `handleSend()`: validates non-empty, appends user message, sends WS message, clears input
- Auto-scrolls to bottom on new message

**Incoming message handling** (via `useEffect` on `lastMessage`):
- `chat_response` → append assistant message to `messages`, set `sending = false`
- `error` → append error message styled differently

**Placeholder state** (Unit 1):
- Shows "JARVIS is ready. Say hello!" as initial empty state message

---

### VoiceIndicator (`components/VoiceIndicator.tsx`)

**Props**: none (reads from WebSocketContext)

**Unit 1 state**: Renders a disabled microphone icon button.

```typescript
// Unit 1: placeholder — no voice logic yet
<button disabled title="Voice coming soon">
  <MicOffIcon />
</button>
```

Full implementation in Unit 2.

---

### StatsSidebar (`components/StatsSidebar.tsx`)

**Props**:
```typescript
interface StatsSidebarProps {
  stats: SystemStats | null
}
```

**Unit 1 rendering**:
```typescript
if (!stats) return <div className="stats-sidebar stats-loading">
  <p>System stats loading...</p>
  <SkeletonBar />  // placeholder skeleton
  <SkeletonBar />
  <SkeletonBar />
</div>
```

Full implementation in Unit 4.

---

### NotificationBar (`components/NotificationBar.tsx`)

**Props**:
```typescript
interface NotificationBarProps {
  notifications: Notification[]
  onDismiss: (id: string) => void
}
```

**Unit 1 rendering**: Returns `null` when `notifications` is empty (zero height, no layout impact).

Full implementation in Unit 4.

---

### CalendarPanel (`components/CalendarPanel.tsx`)

**Props**: none

**Unit 1 rendering**:
```typescript
<div className="calendar-panel">
  <h2>Calendar & Tasks</h2>
  <p>Task management coming soon.</p>
</div>
```

Full implementation in Unit 7.

---

## Shared TypeScript Types (`types/index.ts`)

```typescript
export interface WSMessage {
  type: string
  payload: unknown
  timestamp: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'error'
  content: string
  type: 'text' | 'code'
  language?: string
  timestamp: string
}

export interface SystemStats {
  cpu_percent: number
  ram_percent: number
  ram_used_gb: number
  ram_total_gb: number
  disk_percent: number
  disk_used_gb: number
  disk_total_gb: number
  battery_level: number | null
  battery_charging: boolean | null
  network_connected: boolean
  timestamp: string
}

export interface Notification {
  id: string
  type: string
  message: string
  severity: 'info' | 'warning' | 'critical'
  timestamp: string
}

export interface Task {
  id: string
  title: string
  date: string
  description: string
  created_at: string
}
```

---

## UI/UX Specifications

### Layout
- **Background**: Dark theme (`#1a1a2e` or similar dark navy)
- **NotificationBar**: Full-width top strip, `z-index` above main content
- **Main layout**: CSS flexbox row — ChatPanel takes remaining width, StatsSidebar fixed at 280px
- **ChatPanel**: Flex column — messages list scrollable, input area fixed at bottom
- **CalendarPanel**: Slide-in panel from right or modal overlay

### Message Bubbles
- User messages: right-aligned, accent color background
- Assistant messages: left-aligned, darker card background
- Error messages: left-aligned, red/warning color

### Connection Indicator
- Small dot in header/corner: green = connected, red = disconnected, yellow = reconnecting
- Text label: "Connected" / "Disconnected" / "Reconnecting..."

### Responsive Breakpoints
- `>= 1024px`: full layout (chat + sidebar)
- `< 1024px`: sidebar collapses to icon strip or hidden behind toggle
