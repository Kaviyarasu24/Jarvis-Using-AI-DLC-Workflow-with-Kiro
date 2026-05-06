import { useEffect, useRef } from 'react'
import {
  Globe,
  MessageSquare,
  CheckSquare,
  Terminal,
  Code2,
  Mic,
} from 'lucide-react'

export interface IntentOption {
  id: string          // matches backend intent key
  label: string       // display name
  description: string // short hint
  icon: React.ReactNode
  color: string       // tailwind text color class
}

export const INTENT_OPTIONS: IntentOption[] = [
  {
    id: 'browser',
    label: 'browser',
    description: 'Search the web & summarize',
    icon: <Globe size={14} />,
    color: 'text-blue-400',
  },
  {
    id: 'chat',
    label: 'chat',
    description: 'General conversation with JARVIS',
    icon: <MessageSquare size={14} />,
    color: 'text-jarvis-accent-light',
  },
  {
    id: 'task',
    label: 'task',
    description: 'Add, view or remove tasks',
    icon: <CheckSquare size={14} />,
    color: 'text-green-400',
  },
  {
    id: 'system',
    label: 'system',
    description: 'Open apps, files, run commands',
    icon: <Terminal size={14} />,
    color: 'text-yellow-400',
  },
  {
    id: 'code',
    label: 'code',
    description: 'Generate, debug or review code',
    icon: <Code2 size={14} />,
    color: 'text-purple-400',
  },
  {
    id: 'voice',
    label: 'voice',
    description: 'Enable or disable voice mode',
    icon: <Mic size={14} />,
    color: 'text-pink-400',
  },
]

interface IntentPickerProps {
  query: string           // text after the @ sign (for filtering)
  onSelect: (intent: IntentOption) => void
  onDismiss: () => void
}

export default function IntentPicker({ query, onSelect, onDismiss }: IntentPickerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const activeRef = useRef<HTMLButtonElement>(null)

  const filtered = INTENT_OPTIONS.filter(o =>
    o.id.startsWith(query.toLowerCase()) || o.label.startsWith(query.toLowerCase())
  )

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onDismiss()
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [onDismiss])

  // Scroll active item into view
  useEffect(() => {
    activeRef.current?.scrollIntoView({ block: 'nearest' })
  }, [query])

  if (filtered.length === 0) return null

  return (
    <div
      ref={containerRef}
      role="listbox"
      aria-label="Intent picker"
      className="absolute bottom-full mb-2 right-0 w-64 bg-jarvis-card border border-jarvis-border/60 rounded-xl shadow-2xl overflow-hidden z-50 backdrop-blur-md"
    >
      {/* Header */}
      <div className="px-3 py-2 border-b border-jarvis-border/40">
        <span className="text-[10px] text-jarvis-muted uppercase tracking-widest font-medium">
          Route to intent
        </span>
      </div>

      {/* Options */}
      <div className="py-1 max-h-56 overflow-y-auto">
        {filtered.map((option, idx) => (
          <button
            key={option.id}
            ref={idx === 0 ? activeRef : undefined}
            role="option"
            aria-selected={false}
            onClick={() => onSelect(option)}
            className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-jarvis-surface/60 transition-colors text-left group"
          >
            {/* Icon */}
            <span className={`flex-shrink-0 ${option.color}`}>
              {option.icon}
            </span>

            {/* Text */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className={`text-sm font-medium ${option.color}`}>
                  @{option.label}
                </span>
              </div>
              <p className="text-[11px] text-jarvis-muted truncate leading-tight mt-0.5">
                {option.description}
              </p>
            </div>
          </button>
        ))}
      </div>

      {/* Footer hint */}
      <div className="px-3 py-1.5 border-t border-jarvis-border/40">
        <span className="text-[10px] text-jarvis-muted">
          Press <kbd className="px-1 py-0.5 rounded bg-jarvis-surface text-jarvis-muted text-[9px]">Esc</kbd> to dismiss
        </span>
      </div>
    </div>
  )
}
