# Unit 7: Calendar & Tasks — Business Logic Model

## 1. Natural Language Command Parsing

```
parse_calendar_intent(message) -> CalendarIntent:
  msg_lower = message.lower()
  
  # Add task
  IF any trigger in ["add task", "remind me", "schedule", "add reminder", "create task"]:
    title = extract_title(message)
    date = extract_date(message)  # default: today
    description = extract_description(message)
    RETURN CalendarIntent(action="add", title=title, date=date, description=description)
  
  # Remove task
  IF any trigger in ["remove task", "delete task", "cancel reminder", "remove reminder"]:
    title = extract_title(message)
    RETURN CalendarIntent(action="remove", title=title)
  
  # View today
  IF any trigger in ["today", "what do i have today", "today's tasks"]:
    RETURN CalendarIntent(action="view", date="today")
  
  # View tomorrow
  IF "tomorrow" in message:
    RETURN CalendarIntent(action="view", date="tomorrow")
  
  # Reminders
  IF any trigger in ["reminder", "coming up", "upcoming"]:
    RETURN CalendarIntent(action="reminders")
  
  # General view
  IF any trigger in ["show tasks", "list tasks", "my schedule", "what's on"]:
    RETURN CalendarIntent(action="view", date="all")
  
  DEFAULT: RETURN CalendarIntent(action="view", date="all")
```

## 2. Date Parsing

```
parse_date(date_str) -> str:  # returns "YYYY-MM-DD"
  today = date.today()
  
  IF date_str == "today": RETURN today.isoformat()
  IF date_str == "tomorrow": RETURN (today + timedelta(1)).isoformat()
  IF date_str matches "YYYY-MM-DD": RETURN date_str
  IF date_str matches "DD/MM/YYYY": RETURN reformat to "YYYY-MM-DD"
  IF date_str is a day name ("Monday", "Tuesday", ...):
    RETURN next occurrence of that weekday
  
  DEFAULT: RETURN today.isoformat()
```

## 3. Task CRUD Operations

```
add_task(title, date, description="") -> Task:
  task = Task(id=uuid4(), title=title, date=date, description=description, created_at=now())
  tasks.append(task)
  save_tasks()
  RETURN task

remove_task(task_id=None, title=None) -> bool:
  IF task_id: remove task where task.id == task_id
  IF title: remove task where task.title.lower() == title.lower() (first match)
  save_tasks()
  RETURN True if removed, False if not found

get_tasks_for_date(date) -> list[Task]:
  RETURN [t for t in tasks if t.date == date]

get_today_tasks() -> list[Task]:
  RETURN get_tasks_for_date(today.isoformat())

get_tomorrow_tasks() -> list[Task]:
  RETURN get_tasks_for_date((today + timedelta(1)).isoformat())

get_reminders() -> list[Task]:
  RETURN get_today_tasks() + get_tomorrow_tasks()
```

## 4. Chat Response Formatting

```
format_task_list(tasks, label) -> str:
  IF tasks is empty:
    RETURN f"No tasks {label}."
  lines = [f"• {t.title} ({t.date})" + (f" — {t.description}" if t.description else "")
           for t in tasks]
  RETURN f"Tasks {label}:\n" + "\n".join(lines)
```
