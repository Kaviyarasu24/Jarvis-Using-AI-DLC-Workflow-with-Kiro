import { useEffect, useRef, useState, useCallback } from 'react'
import { Send, Copy, Check, Square, Trash2 } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useWebSocket } from '../context/WebSocketContext'
import VoiceIndicator from './VoiceIndicator'
import JarvisRing from './JarvisRing'
import NewsPanel from './NewsPanel'
import IntentPicker, { INTENT_OPTIONS } from './IntentPicker'
import type { IntentOption } from './IntentPicker'
import type { Message, ChatResponsePayload } from '../types'

// ── Intent helpers ────────────────────────────────────────────────────────────

/** Map frontend intent labels → backend intent keys */
const INTENT_TO_BACKEND: Record<string, string> = {
  browser: 'search',
  chat: 'chat',
  task: 'calendar',
  system: 'system',
  code: 'code',
  voice: 'voice_control',
}

/**
 * Parse an @intent prefix from the raw input.
 * Returns { intent, cleanText } where intent is the backend key (or null).
 * e.g. "@browser what are today's prices" → { intent: "search", cleanText: "what are today's prices" }
 */
function parseAtIntent(raw: string): { intent: string | null; cleanText: string } {
  const match = raw.match(/^@(\w+)\s*(.*)$/s)
  if (!match) return { intent: null, cleanText: raw }
  const label = match[1].toLowerCase()
  const rest = match[2].trim()
  // Accept both the frontend label and the backend key directly
  const backendIntent =
    INTENT_TO_BACKEND[label] ??
    (Object.values(INTENT_TO_BACKEND).includes(label) ? label : null)
  return { intent: backendIntent, cleanText: rest || raw }
}

/** Render the @intent badge shown inside the user message bubble */
function IntentBadge({ label }: { label: string }) {
  const option = INTENT_OPTIONS.find(o => INTENT_TO_BACKEND[o.id] === label || o.id === label)
  if (!option) return null
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-jarvis-surface border border-jarvis-border/60 mr-1.5 align-middle ${option.color}`}
    >
      {option.icon}
      @{option.label}
    </span>
  )
}

function generateId(): string {
  return crypto.randomUUID()
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

function CodeBlock({ content, language }: { content: string; language: string }) {
  const [copied, setCopied] = useState(false)
  const codeMatch = content.match(/```\w*\n?([\s\S]*?)```/)
  const code = codeMatch ? codeMatch[1].trim() : content

  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <div className="w-full rounded-xl overflow-hidden border border-jarvis-border">
      <div className="flex items-center justify-between px-3 py-1.5 bg-jarvis-bg border-b border-jarvis-border">
        <span className="text-xs text-jarvis-muted font-mono">{language}</span>
        <button
          data-testid="code-copy-btn"
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-jarvis-muted hover:text-jarvis-text transition-colors"
          aria-label="Copy code"
        >
          {copied ? <Check size={12} className="text-jarvis-success" /> : <Copy size={12} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <SyntaxHighlighter
        language={language}
        style={atomDark}
        customStyle={{ margin: 0, borderRadius: 0, fontSize: '0.8rem', background: '#0d1117' }}
        wrapLongLines
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}

function CopyTextButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }
  return (
    <button
      onClick={handleCopy}
      className="opacity-0 group-hover:opacity-60 hover:!opacity-100 text-jarvis-muted transition-all ml-1 flex-shrink-0"
      aria-label="Copy message"
      title="Copy message"
    >
      {copied ? <Check size={11} className="text-jarvis-success" /> : <Copy size={11} />}
    </button>
  )
}

function MessageBubble({ message, onDelete }: { message: Message & { intent?: string }; onDelete: (id: string) => void }) {
  const isUser = message.role === 'user'
  const isError = message.role === 'error'
  const isStreaming = message.role === 'assistant' && (message as Message & { streaming?: boolean }).streaming

  return (
    <div
      data-testid={`message-${message.id}`}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 group`}
    >
      {message.type === 'code' && !isUser ? (
        <div className="w-full max-w-[90%]">
          <CodeBlock content={message.content} language={message.language || 'text'} />
          <div className="flex items-center justify-between mt-1 px-1">
            <span className="text-[10px] text-jarvis-muted">{formatTime(message.timestamp)}</span>
            <button
              data-testid={`delete-msg-${message.id}`}
              onClick={() => onDelete(message.id)}
              className="opacity-0 group-hover:opacity-60 hover:!opacity-100 text-jarvis-muted hover:text-jarvis-danger transition-all"
              aria-label="Delete message"
              title="Delete message"
            >
              <Trash2 size={11} />
            </button>
          </div>
        </div>
      ) : (
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[75%]`}>
          <div className={`flex items-end gap-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
            <div
              className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                isUser
                  ? 'bg-jarvis-accent text-white rounded-br-sm'
                  : isError
                  ? 'bg-jarvis-danger/20 text-jarvis-danger border border-jarvis-danger/30 rounded-bl-sm'
                  : 'bg-jarvis-card text-jarvis-text border border-jarvis-border rounded-bl-sm'
              }`}
            >
              {/* Show @intent badge on user messages that had an explicit intent */}
              {isUser && message.intent && <IntentBadge label={message.intent} />}
              {message.content}
              {isStreaming && (
                <span className="inline-block w-1.5 h-3.5 bg-jarvis-accent-light ml-0.5 animate-pulse rounded-sm" />
              )}
            </div>
            {/* Copy button for assistant messages */}
            {!isUser && !isError && message.content && (
              <CopyTextButton text={message.content} />
            )}
          </div>
          {/* Timestamp + delete row */}
          <div className={`flex items-center gap-2 mt-0.5 px-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
            <span className="text-[10px] text-jarvis-muted">{formatTime(message.timestamp)}</span>
            <button
              data-testid={`delete-msg-${message.id}`}
              onClick={() => onDelete(message.id)}
              className="opacity-0 group-hover:opacity-50 hover:!opacity-100 text-jarvis-muted hover:text-jarvis-danger transition-all"
              aria-label="Delete message"
              title="Delete message"
            >
              <Trash2 size={11} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ChatPanel() {
  const { sendMessage, lastMessage } = useWebSocket()
  const [messages, setMessages] = useState<(Message & { intent?: string })[]>([
    {
      id: generateId(),
      role: 'assistant',
      content: 'JARVIS is ready. Say hello! 👋',
      type: 'text',
      timestamp: new Date().toISOString(),
    },
  ])
  const [inputText, setInputText] = useState('')
  const [sending, setSending] = useState(false)
  const [inputExpanded, setInputExpanded] = useState(false)
  const [pendingConfirmation, setPendingConfirmation] = useState<{
    action_id: string
    action: string
    details: string
  } | null>(null)
  // @ intent picker state
  const [pickerOpen, setPickerOpen] = useState(false)
  const [pickerQuery, setPickerQuery] = useState('')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const streamingIdRef = useRef<Map<string, string>>(new Map())

  const isNearBottom = useCallback(() => {
    const container = messagesEndRef.current?.parentElement
    if (!container) return true
    return container.scrollHeight - container.scrollTop - container.clientHeight < 120
  }, [])

  useEffect(() => {
    if (isNearBottom()) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isNearBottom])

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    // ── Streaming: start ──────────────────────────────────────────────────
    if (lastMessage.type === 'stream_start') {
      const { id: streamId } = lastMessage.payload as { id: string }
      const msgId = generateId()
      streamingIdRef.current.set(streamId, msgId)
      setMessages(prev => [
        ...prev,
        {
          id: msgId,
          role: 'assistant',
          content: '',
          type: 'text',
          timestamp: lastMessage.timestamp,
          streaming: true,
        } as Message & { streaming: boolean },
      ])
      setSending(false) // hide typing indicator — streaming bubble is visible
    }

    // ── Streaming: token ──────────────────────────────────────────────────
    else if (lastMessage.type === 'stream_token') {
      const { id: streamId, token, done } = lastMessage.payload as {
        id: string; token: string; done: boolean
      }
      const msgId = streamingIdRef.current.get(streamId)
      if (!msgId) return
      setMessages(prev => prev.map(m =>
        m.id === msgId
          ? { ...m, content: m.content + token, streaming: !done } as Message & { streaming: boolean }
          : m
      ))
      if (done) streamingIdRef.current.delete(streamId)
    }

    // ── Streaming: cancelled ──────────────────────────────────────────────
    else if (lastMessage.type === 'stream_end') {
      const { id: streamId } = lastMessage.payload as { id: string; cancelled?: boolean }
      const msgId = streamingIdRef.current.get(streamId)
      if (msgId) {
        setMessages(prev => prev.map(m =>
          m.id === msgId ? { ...m, streaming: false } as Message & { streaming: boolean } : m
        ))
        streamingIdRef.current.delete(streamId)
      }
    }

    // ── Regular (non-streaming) response ──────────────────────────────────
    else if (lastMessage.type === 'chat_response') {
      const payload = lastMessage.payload as ChatResponsePayload
      setMessages(prev => [
        ...prev,
        {
          id: generateId(),
          role: 'assistant',
          content: payload.text,
          type: payload.message_type ?? 'text',
          language: payload.language,
          timestamp: lastMessage.timestamp,
        },
      ])
      setSending(false)
    }

    else if (lastMessage.type === 'error') {
      const payload = lastMessage.payload as { message: string }
      setMessages(prev => [
        ...prev,
        {
          id: generateId(),
          role: 'error',
          content: `Error: ${payload.message}`,
          type: 'text',
          timestamp: lastMessage.timestamp,
        },
      ])
      setSending(false)
    }

    else if (lastMessage.type === 'confirmation_required') {
      const payload = lastMessage.payload as { action_id: string; action: string; details: string }
      setPendingConfirmation(payload)
      setSending(false)
    }
  }, [lastMessage])

  const handleStop = useCallback(async () => {
    try {
      await fetch('http://localhost:8000/api/cancel', { method: 'POST' })
    } catch {
      // ignore
    }
    setSending(false)
    // Mark any in-progress streaming message as stopped
    streamingIdRef.current.forEach((msgId) => {
      setMessages(prev => prev.map(m =>
        m.id === msgId
          ? { ...m, content: m.content || 'Generation stopped.', streaming: false } as Message & { streaming: boolean }
          : m
      ))
    })
    streamingIdRef.current.clear()
  }, [])

  const handleSend = useCallback(() => {
    const raw = inputText.trim()
    if (!raw || sending) return

    const { intent, cleanText } = parseAtIntent(raw)

    // Display the clean text (without @intent prefix) in the chat bubble,
    // but attach the intent label so the badge renders
    setMessages(prev => [
      ...prev,
      {
        id: generateId(),
        role: 'user',
        content: cleanText,
        type: 'text',
        timestamp: new Date().toISOString(),
        intent: intent ?? undefined,
      },
    ])

    // Send to backend — include forced_intent so the router skips LLM classification
    sendMessage('user_message', {
      text: cleanText,
      ...(intent ? { forced_intent: intent } : {}),
    })

    setInputText('')
    setPickerOpen(false)
    setSending(true)
    inputRef.current?.focus()
  }, [inputText, sending, sendMessage])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Escape dismisses the picker
      if (e.key === 'Escape' && pickerOpen) {
        e.preventDefault()
        setPickerOpen(false)
        return
      }
      // Tab or ArrowDown/Up while picker is open — let picker handle it (future)
      if (pickerOpen && (e.key === 'Tab' || e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
        e.preventDefault()
        return
      }
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        if (pickerOpen) {
          // Enter while picker open → dismiss picker, don't send yet
          setPickerOpen(false)
          return
        }
        handleSend()
      }
    },
    [handleSend, pickerOpen]
  )

  const handleConfirm = useCallback(() => {
    if (!pendingConfirmation) return
    sendMessage('confirm_action', { action_id: pendingConfirmation.action_id })
    setMessages(prev => [...prev, {
      id: generateId(),
      role: 'user',
      content: `✓ Confirmed: ${pendingConfirmation.details}`,
      type: 'text',
      timestamp: new Date().toISOString(),
    }])
    setPendingConfirmation(null)
    setSending(true)
  }, [pendingConfirmation, sendMessage])

  const handleDenyConfirmation = useCallback(() => {
    setMessages(prev => [...prev, {
      id: generateId(),
      role: 'assistant',
      content: 'Action cancelled.',
      type: 'text',
      timestamp: new Date().toISOString(),
    }])
    setPendingConfirmation(null)
  }, [])

  // Check if any message is currently streaming
  const isStreaming = streamingIdRef.current.size > 0

  const handleDeleteMessage = useCallback((id: string) => {
    setMessages(prev => prev.filter(m => m.id !== id))
  }, [])

  // ── @ intent picker ───────────────────────────────────────────────────────
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value
    setInputText(val)

    // Detect "@" at the start of the input (or after clearing to "@")
    const atMatch = val.match(/^@(\w*)$/)
    if (atMatch) {
      setPickerQuery(atMatch[1])
      setPickerOpen(true)
    } else if (!val.startsWith('@')) {
      setPickerOpen(false)
    }
  }, [])

  const handleIntentSelect = useCallback((option: IntentOption) => {
    // Replace whatever is in the input with "@label " ready for the user to type their query
    setInputText(`@${option.label} `)
    setPickerOpen(false)
    setInputExpanded(true)
    // Focus and move cursor to end
    requestAnimationFrame(() => {
      if (inputRef.current) {
        inputRef.current.focus()
        const len = inputRef.current.value.length
        inputRef.current.setSelectionRange(len, len)
      }
    })
  }, [])

  return (
    <div
      data-testid="chat-panel"
      className="flex flex-col flex-1 min-h-0 bg-jarvis-surface relative"
    >
      {/* Messages list */}
      {/* Messages list — right-aligned floating card, full height */}
      <div className="flex-1 relative overflow-hidden">
        {/* JARVIS ring — centered background */}
        <div
          className="absolute inset-0 flex items-center justify-center pointer-events-none transition-opacity duration-500"
          style={{ opacity: messages.length > 4 ? 0 : messages.length > 1 ? 0.15 : 1 }}
        >
          <JarvisRing active={sending || isStreaming} size={180} />
        </div>

        {/* News panel — left side */}
        <NewsPanel />

        {/* Floating chat card — right side, full height */}
        <div className="absolute top-4 right-6 bottom-20 w-[400px] flex flex-col bg-jarvis-card/80 backdrop-blur-sm border border-jarvis-border/40 rounded-2xl shadow-xl overflow-hidden z-10">
          {/* Scrollable messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-1">
            {messages.map(msg => (
              <MessageBubble key={msg.id} message={msg} onDelete={handleDeleteMessage} />
            ))}
            {sending && !isStreaming && (
              <div className="flex justify-start mb-3">
                <div className="bg-jarvis-surface border border-jarvis-border rounded-2xl rounded-bl-sm px-4 py-2.5">
                  <span className="flex gap-1 items-center text-jarvis-muted text-sm">
                    <span className="animate-bounce delay-0">●</span>
                    <span className="animate-bounce delay-150">●</span>
                    <span className="animate-bounce delay-300">●</span>
                  </span>
                </div>
              </div>
            )}
            {pendingConfirmation && (
              <div data-testid="confirmation-dialog" className="flex justify-start mb-3">
                <div className="bg-jarvis-warning/10 border border-jarvis-warning/40 rounded-2xl rounded-bl-sm px-4 py-3 max-w-[90%]">
                  <p className="text-jarvis-warning text-sm font-medium mb-1">⚠ Confirmation Required</p>
                  <p className="text-jarvis-text text-sm mb-3">{pendingConfirmation.details}</p>
                  <div className="flex gap-2">
                    <button data-testid="confirm-yes-btn" onClick={handleConfirm}
                      className="px-3 py-1 text-xs bg-jarvis-danger text-white rounded-lg hover:bg-jarvis-danger/80 transition-colors">
                      Confirm
                    </button>
                    <button data-testid="confirm-no-btn" onClick={handleDenyConfirmation}
                      className="px-3 py-1 text-xs bg-jarvis-card border border-jarvis-border text-jarvis-muted rounded-lg hover:text-jarvis-text transition-colors">
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Floating input bar — bottom right, expands on hover */}
      <div
        className="absolute bottom-6 right-6 z-10"
        onMouseEnter={() => setInputExpanded(true)}
        onMouseLeave={() => { if (!inputText.trim() && document.activeElement !== inputRef.current) setInputExpanded(false) }}
      >
        {/* @ Intent Picker — floats above the input bar */}
        {pickerOpen && (
          <IntentPicker
            query={pickerQuery}
            onSelect={handleIntentSelect}
            onDismiss={() => setPickerOpen(false)}
          />
        )}

        {/* Active @intent indicator strip */}
        {(() => {
          const { intent } = parseAtIntent(inputText)
          const option = intent
            ? INTENT_OPTIONS.find(o => INTENT_TO_BACKEND[o.id] === intent || o.id === intent)
            : null
          return option && inputExpanded ? (
            <div className={`flex items-center gap-1.5 mb-1 px-3 py-1 rounded-full bg-jarvis-surface border border-jarvis-border/50 text-[11px] ${option.color} w-fit ml-auto`}>
              {option.icon}
              <span>Routing to <strong>@{option.label}</strong></span>
              <button
                onClick={() => { setInputText(''); setPickerOpen(false) }}
                className="ml-1 opacity-60 hover:opacity-100 text-jarvis-muted"
                aria-label="Clear intent"
              >×</button>
            </div>
          ) : null
        })()}

        <div
          className="flex flex-row items-center bg-jarvis-card/95 backdrop-blur-md border border-jarvis-border/60 rounded-full shadow-2xl"
          style={{
            height: '44px',
            width: inputExpanded ? '400px' : '44px',
            transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
            overflow: 'hidden',
            padding: '0 6px',
            gap: '6px',
          }}
        >
          {/* Textarea — grows to fill available space */}
          <textarea
            ref={inputRef}
            data-testid="chat-input"
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setInputExpanded(true)}
            placeholder="Message JARVIS… or type @ to pick intent"
            rows={1}
            className="bg-transparent text-sm text-jarvis-text placeholder-jarvis-muted focus:outline-none resize-none"
            style={{
              flex: 1,
              minWidth: 0,
              height: '28px',
              lineHeight: '28px',
              paddingTop: 0,
              paddingBottom: 0,
              paddingLeft: '8px',
              opacity: inputExpanded ? 1 : 0,
              transition: 'opacity 0.2s ease 0.15s',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
            }}
          />

          {/* Send / Stop */}
          {(sending || isStreaming) ? (
            <button
              data-testid="chat-stop-btn"
              onClick={handleStop}
              className="flex-shrink-0 w-8 h-8 rounded-full bg-jarvis-danger/20 border border-jarvis-danger/40 text-jarvis-danger hover:bg-jarvis-danger/30 transition-colors flex items-center justify-center"
              style={{ opacity: inputExpanded ? 1 : 0, transition: 'opacity 0.2s ease 0.15s' }}
              aria-label="Stop"
            >
              <Square size={13} />
            </button>
          ) : (
            <button
              data-testid="chat-send-btn"
              onClick={handleSend}
              disabled={!inputText.trim()}
              className="flex-shrink-0 w-8 h-8 rounded-full bg-jarvis-accent text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-jarvis-accent/80 transition-colors flex items-center justify-center"
              style={{ opacity: inputExpanded ? 1 : 0, transition: 'opacity 0.2s ease 0.15s' }}
              aria-label="Send"
            >
              <Send size={13} />
            </button>
          )}

          {/* Mic — always visible, anchors the pill */}
          <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
            <VoiceIndicator
              onTranscript={(text) => {
                setInputText(text)
                setInputExpanded(true)
                inputRef.current?.focus()
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
