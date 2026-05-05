// ============================================================
// JARVIS — Shared TypeScript Types
// ============================================================

/** WebSocket message envelope — all WS messages use this shape */
export interface WSMessage {
  type: string
  payload: unknown
  timestamp: string
}

/** A single message in the chat conversation */
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'error'
  content: string
  type: 'text' | 'code'
  language?: string
  timestamp: string
}

/** Live system monitoring stats from the backend */
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

/** A dismissible alert notification */
export interface Notification {
  id: string
  type: string
  message: string
  severity: 'info' | 'warning' | 'critical'
  timestamp: string
}

/** A calendar task */
export interface Task {
  id: string
  title: string
  date: string          // "YYYY-MM-DD"
  description: string
  created_at: string    // ISO 8601
}

/** Voice pipeline status */
export type VoiceStatus =
  | 'idle'
  | 'listening_start'
  | 'listening_end'
  | 'speaking_start'
  | 'speaking_end'
  | 'toggled'

/** WebSocket connection state */
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting'

/** Payload shapes for specific WS message types */
export interface ChatResponsePayload {
  text: string
  message_type: 'text' | 'code'
  language?: string
}

export interface VoiceStatusPayload {
  status: VoiceStatus
  enabled?: boolean
}

export interface ConfirmationPayload {
  action_id: string
  action: string
  details: string
}

export interface ErrorPayload {
  message: string
  code: string
}
