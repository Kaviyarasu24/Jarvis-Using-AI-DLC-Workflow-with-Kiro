# Unit 7: Calendar & Tasks — Domain Entities

## Task
A calendar task or reminder.

```
Task
├── id: str           — UUID
├── title: str        — task title
├── date: str         — "YYYY-MM-DD"
├── description: str  — optional description (default: "")
└── created_at: str   — ISO 8601
```

## TaskStore
The full persisted task collection.

```
TaskStore
└── tasks: list[Task]
```

## TaskFilter
Query filter for task retrieval.

```
TaskFilter: "all" | "today" | "tomorrow" | date_string ("YYYY-MM-DD")
```

## CalendarIntent
Parsed intent from a natural language calendar command.

```
CalendarIntent
├── action: str       — "add" | "remove" | "view" | "reminders"
├── title: str | None
├── date: str | None  — "YYYY-MM-DD"
└── description: str | None
```
