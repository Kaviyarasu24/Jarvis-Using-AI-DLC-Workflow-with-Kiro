import { useEffect, useState, useCallback } from 'react'
import { Mic, MicOff, Volume2 } from 'lucide-react'
import { useWebSocket } from '../context/WebSocketContext'
import type { VoiceStatus, VoiceStatusPayload } from '../types'

export default function VoiceIndicator() {
  const { sendMessage, lastMessage } = useWebSocket()
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>('idle')
  const [micAvailable, setMicAvailable] = useState(true)

  // Handle incoming voice_status WebSocket messages
  useEffect(() => {
    if (!lastMessage || lastMessage.type !== 'voice_status') return
    const payload = lastMessage.payload as VoiceStatusPayload

    switch (payload.status) {
      case 'toggled':
        setVoiceEnabled(payload.enabled ?? false)
        if (!payload.enabled) setVoiceStatus('idle')
        break
      case 'listening_start':
        setVoiceStatus('listening_start')
        break
      case 'listening_end':
        setVoiceStatus('idle')
        break
      case 'speaking_start':
        setVoiceStatus('speaking_start')
        break
      case 'speaking_end':
        setVoiceStatus('idle')
        break
      case 'error':
        if ((payload as { error?: string }).error === 'Microphone not available') {
          setMicAvailable(false)
        }
        setVoiceStatus('idle')
        setVoiceEnabled(false)
        break
    }
  }, [lastMessage])

  const handleToggle = useCallback(() => {
    sendMessage('voice_toggle', { enabled: !voiceEnabled })
  }, [sendMessage, voiceEnabled])

  const isListening = voiceStatus === 'listening_start'
  const isSpeaking = voiceStatus === 'speaking_start'

  const buttonTitle = !micAvailable
    ? 'Microphone not available'
    : voiceEnabled
    ? 'Disable voice mode'
    : 'Enable voice mode'

  return (
    <div data-testid="voice-indicator" className="flex items-center gap-1.5">
      {/* Main toggle button */}
      <button
        data-testid="voice-toggle-btn"
        onClick={handleToggle}
        disabled={!micAvailable}
        title={buttonTitle}
        aria-label={buttonTitle}
        className={`p-2 rounded-full transition-all duration-200 relative ${
          !micAvailable
            ? 'text-jarvis-muted opacity-40 cursor-not-allowed'
            : voiceEnabled
            ? 'text-jarvis-accent-light bg-jarvis-accent/20 hover:bg-jarvis-accent/30'
            : 'text-jarvis-muted hover:text-jarvis-text hover:bg-jarvis-card'
        } ${voiceEnabled && !isListening && !isSpeaking ? 'ring-2 ring-jarvis-accent/40 ring-offset-1 ring-offset-jarvis-surface' : ''}`}
      >
        {!micAvailable ? (
          <MicOff size={18} />
        ) : isSpeaking ? (
          <Volume2 size={18} className="text-jarvis-accent-light" />
        ) : (
          <Mic size={18} />
        )}
      </button>

      {/* Waveform animation when listening */}
      {isListening && (
        <div
          data-testid="voice-waveform"
          className="flex items-center gap-0.5"
          aria-label="Listening..."
        >
          {[0, 1, 2].map(i => (
            <span
              key={i}
              className="waveform-bar"
              style={{ animationDelay: `${i * 100}ms` }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
