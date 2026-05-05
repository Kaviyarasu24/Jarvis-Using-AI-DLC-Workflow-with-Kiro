import { Calendar, Wifi, WifiOff, Radio } from 'lucide-react'
import { WebSocketProvider, useWebSocket } from './context/WebSocketContext'
import ChatPanel from './components/ChatPanel'
import StatsSidebar from './components/StatsSidebar'
import NotificationBar from './components/NotificationBar'
import CalendarPanel from './components/CalendarPanel'
import type { ConnectionStatus } from './types'

// ============================================================
// Connection status indicator
// ============================================================
function ConnectionIndicator({ status }: { status: ConnectionStatus }) {
  const styles: Record<ConnectionStatus, { dot: string; label: string }> = {
    connected: { dot: 'bg-jarvis-success', label: 'Connected' },
    connecting: { dot: 'bg-jarvis-warning animate-pulse', label: 'Connecting...' },
    reconnecting: { dot: 'bg-jarvis-warning animate-pulse', label: 'Reconnecting...' },
    disconnected: { dot: 'bg-jarvis-danger', label: 'Disconnected' },
  }
  const { dot, label } = styles[status]

  return (
    <div
      data-testid="connection-indicator"
      className="flex items-center gap-1.5 text-xs text-jarvis-muted"
    >
      <span className={`w-2 h-2 rounded-full ${dot}`} />
      <span>{label}</span>
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
    systemStats,
    calendarOpen,
    toggleCalendar,
  } = useWebSocket()

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
        <div className="flex items-center gap-3">
          <ConnectionIndicator status={connectionStatus} />
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

      {/* Main content */}
      <main className="flex flex-1 min-h-0 overflow-hidden">
        <ChatPanel />
        <StatsSidebar stats={systemStats} />
      </main>

      {/* Calendar panel overlay */}
      {calendarOpen && <CalendarPanel />}

      {/* Notification toasts — fixed overlay, outside layout flow */}
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
