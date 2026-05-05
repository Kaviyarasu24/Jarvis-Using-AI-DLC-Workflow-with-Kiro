# Unit 7: Calendar & Tasks — NFR Design Patterns

## 1. Atomic JSON Write (same as AICore history)
```python
def save_tasks(self):
    tmp = self._tasks_path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump({"tasks": [asdict(t) for t in self._tasks]}, f, indent=2)
    tmp.replace(self._tasks_path)
```

## 2. Graceful Corruption Recovery
```python
def load_tasks(self):
    try:
        data = json.loads(path.read_text())
        self._tasks = [Task(**t) for t in data.get("tasks", [])]
    except Exception:
        logger.warning("tasks.json corrupted — resetting.")
        self._tasks = []
```

## 3. REST + WebSocket Dual Access
- CalendarPanel uses REST (`/api/tasks*`) for structured CRUD
- Chat commands use WebSocket → CalendarManager.handle() → same CRUD methods
- Both paths share the same in-memory task list and JSON file
