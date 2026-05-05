import { useEffect, useState, useCallback } from 'react'
import { X, Calendar, Plus, Trash2, Bell, ChevronDown } from 'lucide-react'
import { useWebSocket } from '../context/WebSocketContext'
import type { Task } from '../types'

type FilterType = 'all' | 'today' | 'tomorrow' | string

const API_BASE = 'http://localhost:8000'

async function fetchTasks(filter: FilterType): Promise<Task[]> {
  let url = `${API_BASE}/api/tasks`
  if (filter === 'today') url = `${API_BASE}/api/tasks/today`
  else if (filter === 'tomorrow') url = `${API_BASE}/api/tasks/tomorrow`
  else if (filter !== 'all') url = `${API_BASE}/api/tasks/date/${filter}`

  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch tasks')
  const data = await res.json()
  return data.tasks as Task[]
}

async function fetchReminders(): Promise<Task[]> {
  const res = await fetch(`${API_BASE}/api/reminders`)
  if (!res.ok) throw new Error('Failed to fetch reminders')
  const data = await res.json()
  return data.tasks as Task[]
}

async function createTask(title: string, date: string, description: string): Promise<Task> {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, date, description }),
  })
  if (!res.ok) throw new Error('Failed to create task')
  return res.json()
}

async function deleteTask(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/tasks/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete task')
}

export default function CalendarPanel() {
  const { toggleCalendar } = useWebSocket()

  const [tasks, setTasks] = useState<Task[]>([])
  const [reminders, setReminders] = useState<Task[]>([])
  const [filter, setFilter] = useState<FilterType>('all')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newTitle, setNewTitle] = useState('')
  const [newDate, setNewDate] = useState(new Date().toISOString().split('T')[0])
  const [newDescription, setNewDescription] = useState('')
  const [adding, setAdding] = useState(false)

  const loadTasks = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [taskList, reminderList] = await Promise.all([
        fetchTasks(filter),
        fetchReminders(),
      ])
      setTasks(taskList)
      setReminders(reminderList)
    } catch (e) {
      setError('Failed to load tasks. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  const handleAddTask = async () => {
    if (!newTitle.trim()) return
    setAdding(true)
    try {
      await createTask(newTitle.trim(), newDate, newDescription.trim())
      setNewTitle('')
      setNewDescription('')
      setNewDate(new Date().toISOString().split('T')[0])
      setShowAddForm(false)
      await loadTasks()
    } catch {
      setError('Failed to add task.')
    } finally {
      setAdding(false)
    }
  }

  const handleDeleteTask = async (id: string) => {
    try {
      await deleteTask(id)
      await loadTasks()
    } catch {
      setError('Failed to delete task.')
    }
  }

  const today = new Date().toISOString().split('T')[0]
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]

  return (
    <div
      data-testid="calendar-panel"
      className="fixed right-0 top-0 h-full w-80 bg-jarvis-card border-l border-jarvis-border shadow-2xl z-40 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-jarvis-border flex-shrink-0">
        <div className="flex items-center gap-2 text-jarvis-text font-semibold">
          <Calendar size={16} className="text-jarvis-accent-light" />
          Calendar & Tasks
        </div>
        <button
          data-testid="calendar-panel-close"
          onClick={toggleCalendar}
          className="text-jarvis-muted hover:text-jarvis-text transition-colors"
          aria-label="Close calendar panel"
        >
          <X size={16} />
        </button>
      </div>

      {/* Reminders strip */}
      {reminders.length > 0 && (
        <div className="px-3 py-2 bg-jarvis-accent/10 border-b border-jarvis-border flex-shrink-0">
          <div className="flex items-center gap-1.5 text-xs text-jarvis-accent-light font-medium mb-1">
            <Bell size={11} />
            Reminders ({reminders.length})
          </div>
          {reminders.slice(0, 3).map(t => (
            <div key={t.id} className="text-xs text-jarvis-muted truncate">
              • {t.title} <span className="text-jarvis-accent-light">({t.date === today ? 'today' : 'tomorrow'})</span>
            </div>
          ))}
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-1 px-3 py-2 border-b border-jarvis-border flex-shrink-0">
        {(['all', 'today', 'tomorrow'] as FilterType[]).map(f => (
          <button
            key={f}
            data-testid={`filter-${f}`}
            onClick={() => setFilter(f)}
            className={`px-2 py-1 text-xs rounded-lg transition-colors capitalize ${
              filter === f
                ? 'bg-jarvis-accent text-white'
                : 'text-jarvis-muted hover:text-jarvis-text hover:bg-jarvis-surface'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Task list */}
      <div className="flex-1 overflow-y-auto px-3 py-2">
        {error && (
          <p className="text-xs text-jarvis-danger mb-2">{error}</p>
        )}
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-10 bg-jarvis-border rounded-lg animate-pulse" />
            ))}
          </div>
        ) : tasks.length === 0 ? (
          <p className="text-xs text-jarvis-muted text-center mt-8">
            No tasks {filter !== 'all' ? `for ${filter}` : ''}. Add one below!
          </p>
        ) : (
          <div className="space-y-1.5">
            {tasks.map(task => (
              <div
                key={task.id}
                data-testid={`task-item-${task.id}`}
                className="flex items-start gap-2 p-2.5 rounded-lg bg-jarvis-surface border border-jarvis-border group"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-jarvis-text truncate">{task.title}</p>
                  <p className="text-xs text-jarvis-muted">
                    {task.date === today ? '📅 Today' : task.date === tomorrow ? '📅 Tomorrow' : task.date}
                  </p>
                  {task.description && (
                    <p className="text-xs text-jarvis-muted truncate mt-0.5">{task.description}</p>
                  )}
                </div>
                <button
                  data-testid={`task-delete-${task.id}`}
                  onClick={() => handleDeleteTask(task.id)}
                  className="opacity-0 group-hover:opacity-100 text-jarvis-muted hover:text-jarvis-danger transition-all flex-shrink-0 mt-0.5"
                  aria-label={`Delete task: ${task.title}`}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add task form */}
      <div className="border-t border-jarvis-border flex-shrink-0 p-3">
        {!showAddForm ? (
          <button
            data-testid="add-task-btn"
            onClick={() => setShowAddForm(true)}
            className="w-full flex items-center justify-center gap-1.5 py-2 text-xs text-jarvis-muted hover:text-jarvis-accent-light border border-dashed border-jarvis-border hover:border-jarvis-accent/40 rounded-lg transition-colors"
          >
            <Plus size={13} />
            Add Task
          </button>
        ) : (
          <div className="space-y-2">
            <input
              data-testid="task-title-input"
              type="text"
              value={newTitle}
              onChange={e => setNewTitle(e.target.value)}
              placeholder="Task title *"
              className="w-full bg-jarvis-surface border border-jarvis-border rounded-lg px-2.5 py-1.5 text-xs text-jarvis-text placeholder-jarvis-muted focus:outline-none focus:border-jarvis-accent"
              onKeyDown={e => e.key === 'Enter' && handleAddTask()}
              autoFocus
            />
            <input
              data-testid="task-date-input"
              type="date"
              value={newDate}
              onChange={e => setNewDate(e.target.value)}
              className="w-full bg-jarvis-surface border border-jarvis-border rounded-lg px-2.5 py-1.5 text-xs text-jarvis-text focus:outline-none focus:border-jarvis-accent"
            />
            <input
              data-testid="task-description-input"
              type="text"
              value={newDescription}
              onChange={e => setNewDescription(e.target.value)}
              placeholder="Description (optional)"
              className="w-full bg-jarvis-surface border border-jarvis-border rounded-lg px-2.5 py-1.5 text-xs text-jarvis-text placeholder-jarvis-muted focus:outline-none focus:border-jarvis-accent"
            />
            <div className="flex gap-2">
              <button
                data-testid="task-save-btn"
                onClick={handleAddTask}
                disabled={!newTitle.trim() || adding}
                className="flex-1 py-1.5 text-xs bg-jarvis-accent text-white rounded-lg disabled:opacity-40 hover:bg-jarvis-accent/80 transition-colors"
              >
                {adding ? 'Adding...' : 'Add'}
              </button>
              <button
                data-testid="task-cancel-btn"
                onClick={() => { setShowAddForm(false); setNewTitle(''); setNewDescription('') }}
                className="flex-1 py-1.5 text-xs border border-jarvis-border text-jarvis-muted rounded-lg hover:text-jarvis-text transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
