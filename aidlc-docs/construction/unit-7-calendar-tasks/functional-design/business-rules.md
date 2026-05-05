# Unit 7: Calendar & Tasks — Business Rules

## Data Rules

| ID | Rule |
|---|---|
| BR-U7-001 | Tasks SHALL be stored in `data/tasks.json` as a JSON array |
| BR-U7-002 | Tasks SHALL be loaded on startup and saved immediately after every add/remove operation |
| BR-U7-003 | Each task SHALL have a UUID generated automatically on creation |
| BR-U7-004 | Task date SHALL be stored in "YYYY-MM-DD" format |
| BR-U7-005 | Task title is required; description is optional (defaults to empty string) |

## Chat Command Rules

| ID | Rule |
|---|---|
| BR-U7-010 | "add task", "remind me", "schedule" → add task |
| BR-U7-011 | "remove task", "delete task", "cancel reminder" → remove task by title or ID |
| BR-U7-012 | "what's on my schedule", "show tasks", "list tasks" → view tasks |
| BR-U7-013 | "today's tasks", "what do I have today" → view today's tasks |
| BR-U7-014 | "tomorrow's tasks" → view tomorrow's tasks |
| BR-U7-015 | "reminders", "what's coming up" → show today + tomorrow reminders |
| BR-U7-016 | Date parsing SHALL support: "today", "tomorrow", "YYYY-MM-DD", "DD/MM/YYYY", day names ("Monday") |

## REST API Rules

| ID | Rule |
|---|---|
| BR-U7-020 | CalendarPanel SHALL use REST endpoints for task CRUD (not WebSocket) |
| BR-U7-021 | REST endpoints SHALL return JSON responses |
| BR-U7-022 | DELETE by ID SHALL return 404 if task not found |

## Reminder Rules

| ID | Rule |
|---|---|
| BR-U7-030 | Reminders SHALL include all tasks due today and tomorrow |
| BR-U7-031 | Reminders SHALL be shown in CalendarPanel on load |
| BR-U7-032 | Reminders SHALL be accessible via chat: "what are my reminders?" |
