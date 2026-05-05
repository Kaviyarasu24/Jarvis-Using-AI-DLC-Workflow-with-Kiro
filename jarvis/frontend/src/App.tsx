import { Calendar, Radio } from 'lucide-react'
import { useEffect, useState } from 'react'
import { WebSocketProvider, useWebSocket } from './context/WebSocketContext'
import ChatPanel from './components/ChatPanel'
import NotificationBar from './components/NotificationBar'
import CalendarPanel from './components/CalendarPanel'
import type { ConnectionStatus } from './types'

// ============================================================
// Status dot component
// ============================================================
function StatusDot({
  label,
  status,
  testId,
}: {
  label: string
  status: 'online' | 'offline' | 'checking'
  testId?: string
}) {
  const dotClass =
    status === 'online'
      ? 'bg-jarvis-success'
      : status === 'checking'
      ? 'bg-jarvis-warning animate-pulse'
      : 'bg-jarvis-danger'

  return (
    <div
      data-testid={testId}
      className="flex items-center gap-1.5 text-xs text-jarvis-muted"
    >
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotClass}`} />
      <span className="text-jarvis-muted">{label}</span>
      <span
        className={
          status === 'online'
            ? 'text-jarvis-success'
            : status === 'checking'
            ? 'text-jarvis-warning'
            : 'text-jarvis-danger'
        }
      >
        {status === 'online' ? 'Online' : status === 'checking' ? '...' : 'Offline'}
      </span>
    </div>
  )
}

// ============================================================
// Inner app — uses WebSocket context
// ============================================================
function AppInner() {
  const {
    connectionStatus,
    notifications,
    dismissNotification,
    calendarOpen,
    toggleCalendar,
  } = useWebSocket()

  // Ollama status — poll /health every 15s
  const [ollamaStatus, setOllamaStatus] = useState<'online' | 'offline' | 'checking'>('checking')

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch('http://localhost:8000/health', { signal: AbortSignal.timeout(4000) })
        if (res.ok) {
          const data = await res.json()
          // health endpoint returns ollama_model — if reachable, Ollama is up
          setOllamaStatus(data.ollama_model ? 'online' : 'offline')
        } else {
          setOllamaStatus('offline')
        }
      } catch {
        setOllamaStatus('offline')
      }
    }
    check()
    const interval = setInterval(check, 15000)
    return () => clearInterval(interval)
  }, [])

  // Map WebSocket connection status to online/offline
  const serverStatus: 'online' | 'offline' | 'checking' =
    connectionStatus === 'connected'
      ? 'online'
      : connectionStatus === 'connecting' || connectionStatus === 'reconnecting'
      ? 'checking'
      : 'offline'

  return (
    <div
      data-testid="app-root"
      className="h-screen flex flex-col bg-jarvis-bg text-jarvis-text overflow-hidden"
    >
      {/* Top bar */}
      <header className="flex items-center justify-between px-4 py-2 bg-jarvis-surface border-b border-jarvis-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <Radio size={18} className="text-jarvis-accent-light" />
          <span className="font-bold text-jarvis-text tracking-wide">JARVIS</span>
          <span className="text-xs text-jarvis-muted">AI Personal Assistant</span>
        </div>

        <div className="flex items-center gap-4">
          {/* Server status */}
          <StatusDot
            label="Server"
            status={serverStatus}
            testId="connection-indicator"
          />
          {/* Ollama status */}
          <StatusDot
            label="Ollama"
            status={ollamaStatus}
            testId="ollama-indicator"
          />
          {/* Calendar toggle */}
          <button
            data-testid="calendar-toggle-btn"
            onClick={toggleCalendar}
            className={`p-1.5 rounded-lg transition-colors ${
              calendarOpen
                ? 'bg-jarvis-accent text-white'
                : 'text-jarvis-muted hover:text-jarvis-text hover:bg-jarvis-card'
            }`}
            aria-label="Toggle calendar panel"
            title="Calendar & Tasks"
          >
            <Calendar size={16} />
          </button>
        </div>
      </header>

      {/* Main content — full width */}
      <main className="flex flex-1 min-h-0 overflow-hidden">
        <ChatPanel />
      </main>

      {/* Calendar panel overlay */}
      {calendarOpen && <CalendarPanel />}

      {/* Notification toasts — fixed overlay */}
      <NotificationBar notifications={notifications} onDismiss={dismissNotification} />
    </div>
  )
}

// ============================================================
// Root App — wraps with providers
// ============================================================
export default function App() {
  return (
    <WebSocketProvider>
      <AppInner />
    </WebSocketProvider>
  )
}
