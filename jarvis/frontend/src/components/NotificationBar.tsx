import { useEffect, useState } from 'react'
import {
  BatteryCharging,
  BatteryLow,
  BatteryFull,
  BatteryWarning,
  Wifi,
  WifiOff,
  AlertTriangle,
  Info,
  X,
  Volume2,
  VolumeX,
  Volume1,
} from 'lucide-react'
import type { Notification } from '../types'

// Auto-hide duration in ms
const AUTO_HIDE_MS = 10000

interface ToastProps {
  notification: Notification
  onDismiss: (id: string) => void
}

function getIcon(type: string, message?: string) {
  switch (type) {
    case 'battery_connected':    return <BatteryCharging size={18} className="text-jarvis-success flex-shrink-0" />
    case 'battery_disconnected': return <BatteryWarning  size={18} className="text-jarvis-warning flex-shrink-0" />
    case 'battery_high':         return <BatteryFull     size={18} className="text-jarvis-info flex-shrink-0" />
    case 'battery_low':          return <BatteryLow      size={18} className="text-jarvis-danger flex-shrink-0" />
    case 'wifi_connected':       return <Wifi            size={18} className="text-jarvis-success flex-shrink-0" />
    case 'wifi_disconnected':    return <WifiOff         size={18} className="text-jarvis-danger flex-shrink-0" />
    case 'cpu_high':             return <AlertTriangle   size={18} className="text-jarvis-warning flex-shrink-0" />
    case 'volume_muted':         return <VolumeX         size={18} className="text-jarvis-muted flex-shrink-0" />
    case 'volume_unmuted':       return <Volume2         size={18} className="text-jarvis-text flex-shrink-0" />
    case 'volume_changed': {
      // Pick icon based on level in message
      const lvl = parseInt(message?.match(/(\d+)%/)?.[1] ?? '50')
      if (lvl === 0) return <VolumeX  size={18} className="text-jarvis-muted flex-shrink-0" />
      if (lvl < 40)  return <Volume1  size={18} className="text-jarvis-text flex-shrink-0" />
      return               <Volume2  size={18} className="text-jarvis-text flex-shrink-0" />
    }
    default:                     return <Info            size={18} className="text-jarvis-info flex-shrink-0" />
  }
}

function getColors(severity: Notification['severity']) {
  switch (severity) {
    case 'critical': return 'bg-jarvis-danger/15 border-jarvis-danger/50 shadow-jarvis-danger/20'
    case 'warning':  return 'bg-jarvis-warning/15 border-jarvis-warning/50 shadow-jarvis-warning/20'
    default:         return 'bg-jarvis-info/15 border-jarvis-info/50 shadow-jarvis-info/20'
  }
}

function Toast({ notification, onDismiss }: ToastProps) {
  const [visible, setVisible] = useState(false)
  const [leaving, setLeaving] = useState(false)

  useEffect(() => {
    // Slide in
    const showTimer = setTimeout(() => setVisible(true), 10)

    // Start auto-hide
    const hideTimer = setTimeout(() => {
      setLeaving(true)
      setTimeout(() => onDismiss(notification.id), 400)
    }, AUTO_HIDE_MS)

    return () => {
      clearTimeout(showTimer)
      clearTimeout(hideTimer)
    }
  }, [notification.id, onDismiss])

  const handleDismiss = () => {
    setLeaving(true)
    setTimeout(() => onDismiss(notification.id), 400)
  }

  return (
    <div
      data-testid={`toast-${notification.id}`}
      className={`
        flex items-center gap-3 px-5 py-3 rounded-full border shadow-2xl
        backdrop-blur-md w-auto max-w-[480px]
        transition-all duration-300 ease-out cursor-pointer select-none
        ${getColors(notification.severity)}
        ${visible && !leaving
          ? 'opacity-100 translate-y-0 scale-100'
          : 'opacity-0 -translate-y-4 scale-90'
        }
      `}
      onClick={handleDismiss}
      role="alert"
      aria-live="polite"
    >
      {/* Icon */}
      {getIcon(notification.type, notification.message)}

      {/* Message */}
      <p className="text-sm font-medium text-jarvis-text whitespace-nowrap">
        {notification.message}
      </p>

      {/* Time */}
      <span className="text-[10px] text-jarvis-muted whitespace-nowrap">
        {new Date(notification.timestamp).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </span>

      {/* Dismiss button */}
      <button
        onClick={e => { e.stopPropagation(); handleDismiss() }}
        className="text-jarvis-muted hover:text-jarvis-text transition-colors ml-1 flex-shrink-0"
        aria-label="Dismiss"
      >
        <X size={13} />
      </button>

      {/* Progress bar at bottom of pill */}
      <div className="absolute bottom-0 left-4 right-4 h-0.5 rounded-full overflow-hidden opacity-40">
        <div
          className={`h-full ${
            notification.severity === 'critical' ? 'bg-jarvis-danger' :
            notification.severity === 'warning'  ? 'bg-jarvis-warning' :
            'bg-jarvis-info'
          }`}
          style={{ animation: `shrink ${AUTO_HIDE_MS}ms linear forwards` }}
        />
      </div>
    </div>
  )
}

interface NotificationBarProps {
  notifications: Notification[]
  onDismiss: (id: string) => void
}

export default function NotificationBar({ notifications, onDismiss }: NotificationBarProps) {
  if (notifications.length === 0) return null

  return (
    <div
      data-testid="notification-bar"
      className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-2 pointer-events-none"
      aria-label="Notifications"
    >
      {notifications.map(n => (
        <div key={n.id} className="pointer-events-auto relative">
          <Toast notification={n} onDismiss={onDismiss} />
        </div>
      ))}
    </div>
  )
}
