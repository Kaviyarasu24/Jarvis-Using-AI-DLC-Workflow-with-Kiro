import { useEffect, useRef, useState, useCallback } from 'react'
import { Mic, MicOff, Square } from 'lucide-react'

interface VoiceIndicatorProps {
  /** Called with the transcribed text when speech is recognized */
  onTranscript: (text: string) => void
}

// Browser SpeechRecognition API
const SpeechRecognition =
  (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

export default function VoiceIndicator({ onTranscript }: VoiceIndicatorProps) {
  const [listening, setListening] = useState(false)
  const [supported] = useState(() => !!SpeechRecognition)
  const recognitionRef = useRef<any>(null)

  const startListening = useCallback(() => {
    if (!supported || listening) return

    const recognition = new SpeechRecognition()
    recognition.lang = 'en-US'
    recognition.interimResults = true   // show partial results as user speaks
    recognition.continuous = false      // stop after one phrase
    recognition.maxAlternatives = 1

    recognition.onstart = () => setListening(true)

    recognition.onresult = (event: any) => {
      let transcript = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript
      }
      // Pass interim + final results to input box
      onTranscript(transcript)
    }

    recognition.onend = () => {
      setListening(false)
      recognitionRef.current = null
    }

    recognition.onerror = (event: any) => {
      console.warn('Speech recognition error:', event.error)
      setListening(false)
      recognitionRef.current = null
    }

    recognitionRef.current = recognition
    recognition.start()
  }, [supported, listening, onTranscript])

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    setListening(false)
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [])

  if (!supported) {
    return (
      <button
        disabled
        title="Voice input not supported in this browser"
        className="p-2 rounded-full text-jarvis-muted opacity-40 cursor-not-allowed"
        aria-label="Voice input not supported"
      >
        <MicOff size={18} />
      </button>
    )
  }

  return (
    <button
      data-testid="voice-toggle-btn"
      onClick={listening ? stopListening : startListening}
      title={listening ? 'Stop listening' : 'Click to speak'}
      aria-label={listening ? 'Stop voice input' : 'Start voice input'}
      className={`p-2 rounded-full transition-all duration-200 relative flex-shrink-0 ${
        listening
          ? 'text-jarvis-danger bg-jarvis-danger/20 ring-2 ring-jarvis-danger/40 ring-offset-1 ring-offset-transparent'
          : 'text-jarvis-muted hover:text-jarvis-accent-light hover:bg-jarvis-accent/10'
      }`}
    >
      {listening ? (
        <>
          <Square size={16} />
          {/* Pulse ring while listening */}
          <span className="absolute inset-0 rounded-full animate-ping bg-jarvis-danger/20" />
        </>
      ) : (
        <Mic size={18} />
      )}
    </button>
  )
}
