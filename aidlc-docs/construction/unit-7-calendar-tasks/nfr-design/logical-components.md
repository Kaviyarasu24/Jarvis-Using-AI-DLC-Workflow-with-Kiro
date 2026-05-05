# Unit 7: Calendar & Tasks — Logical Components

| Component | Purpose |
|---|---|
| `CalendarManager` | Task CRUD, JSON persistence, NL command parsing, reminder queries |
| `data/tasks.json` | Persistent task storage |
| FastAPI REST routes | `/api/tasks*` endpoints for CalendarPanel |
| `CalendarPanel` (React) | Task list UI, add/remove form, date filter, reminders display |
| `IntentRouter` (Unit 3) | Routes "calendar" intent to CalendarManager |
