import { useEffect, useState, useCallback, useMemo } from 'react'
import {
  X, Calendar, Plus, Trash2, Bell, ChevronLeft, ChevronRight, Check, Clock,
} from 'lucide-react'
import { useWebSocket } from '../context/WebSocketContext'
import type { Task } from '../types'

const API = 'http://localhost:8000'

// ── API helpers ────────────────────────────────────────────────────────────
async function apiFetchTasks(): Promise<Task[]> {
  const res = await fetch(`${API}/api/tasks`)
  if (!res.ok) throw new Error('fetch failed')
  return (await res.json()).tasks as Task[]
}

async function apiCreateTask(
  title: string, date: string, time: string, description: string,
): Promise<Task> {
  const res = await fetch(`${API}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, date, time, description }),
  })
  if (!res.ok) throw new Error('create failed')
  return res.json()
}

async function apiDeleteTask(id: string): Promise<void> {
  await fetch(`${API}/api/tasks/${id}`, { method: 'DELETE' })
}

async function apiCompleteTask(id: string): Promise<void> {
  await fetch(`${API}/api/tasks/${id}/complete`, { method: 'PATCH' })
}

// ── Date helpers ───────────────────────────────────────────────────────────
const toISO = (d: Date) => d.toISOString().split('T')[0]
const todayISO = toISO(new Date())
const tomorrowISO = toISO(new Date(Date.now() + 86400000))

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate()
}
function firstDayOfMonth(year: number, month: number) {
  return new Date(year, month, 1).getDay() // 0=Sun
}

const MONTH_NAMES = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December',
]
const DAY_LABELS = ['Su','Mo','Tu','We','Th','Fr','Sa']

// ── Sub-components ─────────────────────────────────────────────────────────

function TaskDot({ count, completed }: { count: number; completed: number }) {
  if (count === 0) return null
  return (
    <div className="flex gap-0.5 justify-center mt-0.5 flex-wrap">
      {Array.from({ length: Math.min(count, 4) }).map((_, i) => (
        <span
          key={i}
          className={`w-1 h-1 rounded-full ${
            i < completed ? 'bg-green-400' : 'bg-jarvis-accent-light'
          }`}
        />
      ))}
    </div>
  )
}

function TaskItem({
  task,
  onComplete,
  onDelete,
}: {
  task: Task
  onComplete: (id: string) => void
  onDelete: (id: string) => void
}) {
  const isToday = task.date === todayISO
  const isTomorrow = task.date === tomorrowISO

  return (
    <div
      className={`flex items-start gap-2 p-2.5 rounded-lg border group transition-all ${
        task.completed
          ? 'bg-jarvis-surface/40 border-jarvis-border/40 opacity-60'
          : 'bg-jarvis-surface border-jarvis-border'
      }`}
    >
      {/* Complete checkbox */}
      <button
        onClick={() => !task.completed && onComplete(task.id)}
        className={`flex-shrink-0 w-4 h-4 rounded border mt-0.5 flex items-center justify-center transition-colors ${
          task.completed
            ? 'bg-green-500 border-green-500'
            : 'border-jarvis-border hover:border-jarvis-accent'
        }`}
        aria-label={task.completed ? 'Completed' : 'Mark complete'}
      >
        {task.completed && <Check size={10} className="text-white" />}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className={`text-sm truncate ${task.completed ? 'line-through text-jarvis-muted' : 'text-jarvis-text'}`}>
          {task.title}
        </p>
        <div className="flex items-center gap-2 mt-0.5 flex-wrap">
          <span className="text-[10px] text-jarvis-muted">
            {isToday ? '📅 Today' : isTomorrow ? '📅 Tomorrow' : task.date}
          </span>
          {task.time && (
            <span className="flex items-center gap-0.5 text-[10px] text-jarvis-accent-light">
              <Clock size={9} />
              {task.time}
            </span>
          )}
        </div>
        {task.description && (
          <p className="text-[10px] text-jarvis-muted truncate mt-0.5">{task.description}</p>
        )}
      </div>

      {/* Delete */}
      <button
        onClick={() => onDelete(task.id)}
        className="opacity-0 group-hover:opacity-100 text-jarvis-muted hover:text-jarvis-danger transition-all flex-shrink-0 mt-0.5"
        aria-label={`Delete ${task.title}`}
      >
        <Trash2 size={12} />
      </button>
    </div>
  )
}

// ── Add Task Form ──────────────────────────────────────────────────────────

function AddTaskForm({
  defaultDate,
  onAdd,
  onCancel,
}: {
  defaultDate: string
  onAdd: (title: string, date: string, time: string, desc: string) => Promise<void>
  onCancel: () => void
}) {
  const [title, setTitle] = useState('')
  const [date, setDate] = useState(defaultDate)
  const [time, setTime] = useState('')
  const [desc, setDesc] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async () => {
    if (!title.trim()) return
    setSaving(true)
    try {
      await onAdd(title.trim(), date, time, desc.trim())
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-2 p-3 bg-jarvis-surface rounded-xl border border-jarvis-border">
      <input
        autoFocus
        type="text"
        value={title}
        onChange={e => setTitle(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        placeholder="Task title *"
        className="w-full bg-jarvis-card border border-jarvis-border rounded-lg px-2.5 py-1.5 text-xs text-jarvis-text placeholder-jarvis-muted focus:outline-none focus:border-jarvis-accent"
      />

      <div className="flex gap-2">
        {/* Date */}
        <div className="flex-1">
          <label className="text-[10px] text-jarvis-muted block mb-0.5">Date</label>
          <input
            type="date"
            value={date}
            onChange={e => setDate(e.target.value)}
            className="w-full bg-jarvis-card border border-jarvis-border rounded-lg px-2 py-1.5 text-xs text-jarvis-text focus:outline-none focus:border-jarvis-accent"
          />
        </div>
        {/* Time */}
        <div className="flex-1">
          <label className="text-[10px] text-jarvis-muted block mb-0.5">
            Time <span className="opacity-50">(optional)</span>
          </label>
          <input
            type="time"
            value={time}
            onChange={e => setTime(e.target.value)}
            className="w-full bg-jarvis-card border border-jarvis-border rounded-lg px-2 py-1.5 text-xs text-jarvis-text focus:outline-none focus:border-jarvis-accent"
          />
        </div>
      </div>

      <input
        type="text"
        value={desc}
        onChange={e => setDesc(e.target.value)}
        placeholder="Description (optional)"
        className="w-full bg-jarvis-card border border-jarvis-border rounded-lg px-2.5 py-1.5 text-xs text-jarvis-text placeholder-jarvis-muted focus:outline-none focus:border-jarvis-accent"
      />

      {time && (
        <p className="text-[10px] text-jarvis-accent-light flex items-center gap-1">
          <Bell size={9} />
          You'll be reminded at {time} on {date}
        </p>
      )}

      <div className="flex gap-2 pt-1">
        <button
          onClick={handleSubmit}
          disabled={!title.trim() || saving}
          className="flex-1 py-1.5 text-xs bg-jarvis-accent text-white rounded-lg disabled:opacity-40 hover:bg-jarvis-accent/80 transition-colors"
        >
          {saving ? 'Adding…' : 'Add Task'}
        </button>
        <button
          onClick={onCancel}
          className="flex-1 py-1.5 text-xs border border-jarvis-border text-jarvis-muted rounded-lg hover:text-jarvis-text transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

// ── Main Component ─────────────────────────────────────────────────────────

export default function CalendarPanel() {
  const { toggleCalendar } = useWebSocket()

  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)

  // Calendar navigation
  const now = new Date()
  const [viewYear, setViewYear] = useState(now.getFullYear())
  const [viewMonth, setViewMonth] = useState(now.getMonth())
  const [selectedDate, setSelectedDate] = useState<string>(todayISO)

  const loadTasks = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setTasks(await apiFetchTasks())
    } catch {
      setError('Failed to load tasks.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadTasks() }, [loadTasks])

  // Build a map: date → tasks[]
  const tasksByDate = useMemo(() => {
    const map: Record<string, Task[]> = {}
    for (const t of tasks) {
      if (!map[t.date]) map[t.date] = []
      map[t.date].push(t)
    }
    return map
  }, [tasks])

  // Tasks for the selected date
  const selectedTasks = useMemo(
    () => (tasksByDate[selectedDate] ?? []).sort((a, b) => (a.time || '99:99').localeCompare(b.time || '99:99')),
    [tasksByDate, selectedDate],
  )

  // Upcoming reminders (today + future with time set, not completed)
  const reminders = useMemo(
    () => tasks.filter(t => !t.completed && t.time && t.date >= todayISO)
              .sort((a, b) => `${a.date}${a.time}`.localeCompare(`${b.date}${b.time}`))
              .slice(0, 5),
    [tasks],
  )

  // Calendar grid
  const totalDays = daysInMonth(viewYear, viewMonth)
  const firstDay = firstDayOfMonth(viewYear, viewMonth)
  const prevMonth = () => {
    if (viewMonth === 0) { setViewYear(y => y - 1); setViewMonth(11) }
    else setViewMonth(m => m - 1)
  }
  const nextMonth = () => {
    if (viewMonth === 11) { setViewYear(y => y + 1); setViewMonth(0) }
    else setViewMonth(m => m + 1)
  }

  const handleComplete = async (id: string) => {
    await apiCompleteTask(id)
    await loadTasks()
  }

  const handleDelete = async (id: string) => {
    await apiDeleteTask(id)
    await loadTasks()
  }

  const handleAdd = async (title: string, date: string, time: string, desc: string) => {
    await apiCreateTask(title, date, time, desc)
    setShowAddForm(false)
    await loadTasks()
  }

  return (
    <div
      data-testid="calendar-panel"
      className="fixed right-0 top-0 h-full w-80 bg-jarvis-card border-l border-jarvis-border shadow-2xl z-40 flex flex-col overflow-hidden"
    >
      {/* ── Header ── */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-jarvis-border flex-shrink-0">
        <div className="flex items-center gap-2 text-jarvis-text font-semibold text-sm">
          <Calendar size={15} className="text-jarvis-accent-light" />
          Calendar & Tasks
        </div>
        <button onClick={toggleCalendar} className="text-jarvis-muted hover:text-jarvis-text transition-colors" aria-label="Close">
          <X size={15} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">

        {/* ── Calendar Grid ── */}
        <div className="px-3 pt-3 pb-2">
          {/* Month navigation */}
          <div className="flex items-center justify-between mb-2">
            <button onClick={prevMonth} className="p-1 text-jarvis-muted hover:text-jarvis-text transition-colors">
              <ChevronLeft size={14} />
            </button>
            <span className="text-xs font-semibold text-jarvis-text">
              {MONTH_NAMES[viewMonth]} {viewYear}
            </span>
            <button onClick={nextMonth} className="p-1 text-jarvis-muted hover:text-jarvis-text transition-colors">
              <ChevronRight size={14} />
            </button>
          </div>

          {/* Day labels */}
          <div className="grid grid-cols-7 mb-1">
            {DAY_LABELS.map(d => (
              <div key={d} className="text-center text-[9px] text-jarvis-muted font-medium py-0.5">{d}</div>
            ))}
          </div>

          {/* Day cells */}
          <div className="grid grid-cols-7 gap-0.5">
            {/* Empty cells before first day */}
            {Array.from({ length: firstDay }).map((_, i) => (
              <div key={`empty-${i}`} />
            ))}
            {Array.from({ length: totalDays }).map((_, i) => {
              const day = i + 1
              const iso = `${viewYear}-${String(viewMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
              const dayTasks = tasksByDate[iso] ?? []
              const completedCount = dayTasks.filter(t => t.completed).length
              const isToday = iso === todayISO
              const isSelected = iso === selectedDate

              return (
                <button
                  key={iso}
                  onClick={() => setSelectedDate(iso)}
                  className={`relative flex flex-col items-center py-1 rounded-lg text-xs transition-all ${
                    isSelected
                      ? 'bg-jarvis-accent text-white'
                      : isToday
                      ? 'bg-jarvis-accent/20 text-jarvis-accent-light font-semibold'
                      : 'text-jarvis-text hover:bg-jarvis-surface'
                  }`}
                >
                  <span>{day}</span>
                  <TaskDot count={dayTasks.length} completed={completedCount} />
                </button>
              )
            })}
          </div>
        </div>

        {/* ── Upcoming Reminders ── */}
        {reminders.length > 0 && (
          <div className="mx-3 mb-2 p-2.5 rounded-xl bg-jarvis-accent/10 border border-jarvis-accent/20">
            <div className="flex items-center gap-1.5 text-[10px] text-jarvis-accent-light font-semibold mb-1.5 uppercase tracking-wider">
              <Bell size={10} />
              Upcoming Reminders
            </div>
            {reminders.map(t => (
              <div key={t.id} className="flex items-center gap-1.5 text-[11px] text-jarvis-muted py-0.5">
                <Clock size={9} className="text-jarvis-accent-light flex-shrink-0" />
                <span className="truncate">{t.title}</span>
                <span className="text-jarvis-accent-light flex-shrink-0 ml-auto">
                  {t.date === todayISO ? 'today' : t.date === tomorrowISO ? 'tmrw' : t.date.slice(5)} {t.time}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* ── Selected Date Tasks ── */}
        <div className="px-3 pb-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold text-jarvis-text">
              {selectedDate === todayISO
                ? 'Today'
                : selectedDate === tomorrowISO
                ? 'Tomorrow'
                : selectedDate}
              {selectedTasks.length > 0 && (
                <span className="ml-1.5 text-jarvis-muted font-normal">({selectedTasks.length})</span>
              )}
            </span>
            <button
              onClick={() => setShowAddForm(v => !v)}
              className="flex items-center gap-1 text-[10px] text-jarvis-accent-light hover:text-jarvis-accent transition-colors"
            >
              <Plus size={11} />
              Add
            </button>
          </div>

          {/* Add form */}
          {showAddForm && (
            <div className="mb-2">
              <AddTaskForm
                defaultDate={selectedDate}
                onAdd={handleAdd}
                onCancel={() => setShowAddForm(false)}
              />
            </div>
          )}

          {error && <p className="text-xs text-jarvis-danger mb-2">{error}</p>}

          {loading ? (
            <div className="space-y-1.5">
              {[1, 2].map(i => <div key={i} className="h-10 bg-jarvis-border rounded-lg animate-pulse" />)}
            </div>
          ) : selectedTasks.length === 0 ? (
            <p className="text-[11px] text-jarvis-muted text-center py-4">
              No tasks for this day.
            </p>
          ) : (
            <div className="space-y-1.5">
              {selectedTasks.map(task => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onComplete={handleComplete}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
