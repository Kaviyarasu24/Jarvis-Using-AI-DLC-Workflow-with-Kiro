import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react'
import type {
  ConnectionStatus,
  Notification,
  SystemStats,
  WSMessage,
} from '../types'

// ============================================================
// Context value shape
// ============================================================
interface WebSocketContextValue {
  connectionStatus: ConnectionStatus
  sendMessage: (type: string, payload: unknown) => void
  lastMessage: WSMessage | null
  notifications: Notification[]
  systemStats: SystemStats | null
  dismissNotification: (id: string) => void
  calendarOpen: boolean
  toggleCalendar: () => void
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null)

// ============================================================
// Constants
// ============================================================
const WS_URL = 'ws://localhost:8000/ws'
const MAX_RECONNECTS = 5
const BACKOFF_DELAYS_MS = [1000, 2000, 4000, 8000, 16000]

// ============================================================
// Provider
// ============================================================
export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const socketRef = useRef<WebSocket | null>(null)
  const reconnectAttempts = useRef(0)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting')
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [calendarOpen, setCalendarOpen] = useState(false)

  const connect = useCallback(() => {
    // Don't create a new connection if one is already open or connecting
    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) return

    setConnectionStatus('connecting')
    const ws = new WebSocket(WS_URL)
    socketRef.current = ws

    ws.onopen = () => {
      reconnectAttempts.current = 0
      setConnectionStatus('connected')
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const msg: WSMessage = JSON.parse(event.data as string)
        setLastMessage(msg)

        // Handle stats and alerts directly in context
        if (msg.type === 'stats_update') {
          setSystemStats(msg.payload as SystemStats)
        } else if (msg.type === 'alert') {
          const alert = msg.payload as Notification
          const newAlert = { ...alert, id: alert.id ?? crypto.randomUUID() }
          setNotifications(prev => [newAlert, ...prev].slice(0, 10))
          // Auto-remove from state after toast duration + animation buffer
          setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== newAlert.id))
          }, 11000)
        }
      } catch {
        // Ignore malformed messages
      }
    }

    ws.onclose = (event: CloseEvent) => {
      socketRef.current = null
      // Only reconnect on abnormal closes (not clean shutdown)
      if (event.code !== 1000 && reconnectAttempts.current < MAX_RECONNECTS) {
        setConnectionStatus('reconnecting')
        const delay = BACKOFF_DELAYS_MS[
          Math.min(reconnectAttempts.current, BACKOFF_DELAYS_MS.length - 1)
        ]
        reconnectAttempts.current += 1
        reconnectTimer.current = setTimeout(connect, delay)
      } else {
        setConnectionStatus('disconnected')
      }
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      socketRef.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((type: string, payload: unknown) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({ type, payload, timestamp: new Date().toISOString() })
      )
    }
  }, [])

  const dismissNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const toggleCalendar = useCallback(() => {
    setCalendarOpen(prev => !prev)
  }, [])

  return (
    <WebSocketContext.Provider
      value={{
        connectionStatus,
        sendMessage,
        lastMessage,
        notifications,
        systemStats,
        dismissNotification,
        calendarOpen,
        toggleCalendar,
      }}
    >
      {children}
    </WebSocketContext.Provider>
  )
}

// ============================================================
// Hook
// ============================================================
export function useWebSocket(): WebSocketContextValue {
  const ctx = useContext(WebSocketContext)
  if (!ctx) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return ctx
}
