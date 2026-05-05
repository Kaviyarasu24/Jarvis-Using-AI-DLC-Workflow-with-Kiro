# Unit 7: Calendar & Tasks — Code Summary

## Files Created / Modified

| File | Action | Purpose |
|---|---|---|
| `jarvis/backend/calendar_manager.py` | Created | Task CRUD, JSON persistence, NL parsing, reminders |
| `jarvis/backend/main.py` | Modified | Wired CalendarManager, REST endpoints, calendar intent handler |
| `jarvis/backend/tests/test_calendar_manager.py` | Created | 18 tests (CRUD, persistence, NL parsing, date extraction) |
| `jarvis/frontend/src/components/CalendarPanel.tsx` | Modified | Full task management UI (list, add form, delete, filter, reminders) |

## Requirements Covered
FR-060, FR-061, FR-062, FR-063, FR-064, FR-065, NFR-013

## REST Endpoints Added
- GET /api/tasks — all tasks
- GET /api/tasks/today — today's tasks
- GET /api/tasks/tomorrow — tomorrow's tasks
- GET /api/tasks/date/{date} — tasks for specific date
- POST /api/tasks — create task
- DELETE /api/tasks/{id} — delete task
- GET /api/reminders — today + tomorrow reminders

## Key Design Decisions
- Atomic JSON write prevents data loss on shutdown
- Dual access: chat (WebSocket) + UI (REST) share same in-memory store
- NL date parsing: today, tomorrow, YYYY-MM-DD, DD/MM/YYYY, day names
- CalendarPanel shows reminders strip at top, filter tabs, add form at bottom
