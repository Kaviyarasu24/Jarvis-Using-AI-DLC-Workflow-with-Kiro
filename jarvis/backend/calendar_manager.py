"""
CalendarManager — JSON-based local task/calendar management.
Supports CRUD operations, natural language command parsing, and reminders.
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class Task:
    id: str
    title: str
    date: str           # "YYYY-MM-DD"
    description: str
    created_at: str     # ISO 8601


def _today() -> str:
    return date.today().isoformat()


def _tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CalendarManager:
    """Manages local JSON-based tasks with NL command parsing."""

    def __init__(self, config: ConfigManager) -> None:
        self._config = config
        self._tasks: list[Task] = []
        self._tasks_path = Path(config.data_dir) / "tasks.json"
        self.load_tasks()

    # ------------------------------------------------------------------
    # Public: NL command handler (for chat/WebSocket)
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        """Parse natural language calendar command and execute it."""
        intent = self._parse_intent(message)

        if intent["action"] == "add":
            title = intent.get("title", "").strip()
            if not title:
                return {"text": "Please provide a task title. Example: 'add task Buy groceries for tomorrow'", "message_type": "text"}
            task_date = intent.get("date") or _today()
            description = intent.get("description", "")
            task = self.add_task(title, task_date, description)
            return {"text": f"✅ Task added: **{task.title}** on {task.date}", "message_type": "text"}

        elif intent["action"] == "remove":
            title = intent.get("title", "").strip()
            if not title:
                return {"text": "Please specify which task to remove.", "message_type": "text"}
            removed = self.remove_task(title=title)
            if removed:
                return {"text": f"🗑️ Task removed: {title}", "message_type": "text"}
            return {"text": f"No task found with title: '{title}'", "message_type": "text"}

        elif intent["action"] == "view":
            filter_date = intent.get("date", "all")
            if filter_date == "today":
                tasks = self.get_today_tasks()
                return {"text": self._format_task_list(tasks, "for today"), "message_type": "text"}
            elif filter_date == "tomorrow":
                tasks = self.get_tomorrow_tasks()
                return {"text": self._format_task_list(tasks, "for tomorrow"), "message_type": "text"}
            elif filter_date == "all":
                tasks = self.get_all_tasks()
                return {"text": self._format_task_list(tasks, "(all)"), "message_type": "text"}
            else:
                tasks = self.get_tasks_for_date(filter_date)
                return {"text": self._format_task_list(tasks, f"for {filter_date}"), "message_type": "text"}

        elif intent["action"] == "reminders":
            tasks = self.get_reminders()
            return {"text": self._format_reminders(tasks), "message_type": "text"}

        return {"text": "I didn't understand that calendar command. Try: 'add task X for tomorrow', 'show today's tasks', 'remove task X'", "message_type": "text"}

    # ------------------------------------------------------------------
    # Public: CRUD operations
    # ------------------------------------------------------------------

    def add_task(self, title: str, task_date: str, description: str = "") -> Task:
        """Add a new task and persist immediately."""
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            date=task_date,
            description=description,
            created_at=_now_iso(),
        )
        self._tasks.append(task)
        self.save_tasks()
        logger.info(f"Task added: {title!r} on {task_date}")
        return task

    def remove_task(self, task_id: Optional[str] = None, title: Optional[str] = None) -> bool:
        """Remove a task by ID or title. Returns True if removed."""
        original_len = len(self._tasks)
        if task_id:
            self._tasks = [t for t in self._tasks if t.id != task_id]
        elif title:
            title_lower = title.lower()
            self._tasks = [t for t in self._tasks if t.title.lower() != title_lower]
        if len(self._tasks) < original_len:
            self.save_tasks()
            return True
        return False

    def get_all_tasks(self) -> list[Task]:
        return sorted(self._tasks, key=lambda t: t.date)

    def get_tasks_for_date(self, task_date: str) -> list[Task]:
        return [t for t in self._tasks if t.date == task_date]

    def get_today_tasks(self) -> list[Task]:
        return self.get_tasks_for_date(_today())

    def get_tomorrow_tasks(self) -> list[Task]:
        return self.get_tasks_for_date(_tomorrow())

    def get_reminders(self) -> list[Task]:
        """Return tasks due today and tomorrow."""
        return self.get_today_tasks() + self.get_tomorrow_tasks()

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return next((t for t in self._tasks if t.id == task_id), None)

    def tasks_as_dicts(self) -> list[dict]:
        return [asdict(t) for t in self._tasks]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load_tasks(self) -> None:
        try:
            if self._tasks_path.exists():
                data = json.loads(self._tasks_path.read_text(encoding="utf-8"))
                self._tasks = [Task(**t) for t in data.get("tasks", [])]
                logger.info(f"Loaded {len(self._tasks)} tasks.")
            else:
                self._tasks = []
        except Exception as e:
            logger.warning(f"Failed to load tasks.json: {e}. Starting fresh.")
            self._tasks = []

    def save_tasks(self) -> None:
        try:
            tmp = self._tasks_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"tasks": [asdict(t) for t in self._tasks]}, f, indent=2, ensure_ascii=False)
            tmp.replace(self._tasks_path)
        except OSError as e:
            logger.error(f"Failed to save tasks: {e}")

    # ------------------------------------------------------------------
    # Internal: NL parsing
    # ------------------------------------------------------------------

    def _parse_intent(self, message: str) -> dict:
        msg_lower = message.lower()

        # Add task
        if any(t in msg_lower for t in ["add task", "remind me", "schedule", "add reminder", "create task", "new task"]):
            title, task_date, description = self._extract_task_details(message)
            return {"action": "add", "title": title, "date": task_date, "description": description}

        # Remove task
        if any(t in msg_lower for t in ["remove task", "delete task", "cancel reminder", "remove reminder", "delete reminder"]):
            title = self._extract_remove_title(message)
            return {"action": "remove", "title": title}

        # View today
        if any(t in msg_lower for t in ["today's task", "today task", "what do i have today", "tasks today", "schedule today"]):
            return {"action": "view", "date": "today"}

        # View tomorrow
        if "tomorrow" in msg_lower and any(t in msg_lower for t in ["task", "schedule", "reminder"]):
            return {"action": "view", "date": "tomorrow"}

        # Reminders
        if any(t in msg_lower for t in ["reminder", "coming up", "upcoming", "what's due"]):
            return {"action": "reminders"}

        # General view
        if any(t in msg_lower for t in ["show task", "list task", "my schedule", "what's on", "view task", "all task"]):
            return {"action": "view", "date": "all"}

        return {"action": "view", "date": "all"}

    def _extract_task_details(self, message: str) -> tuple[str, str, str]:
        """Extract title, date, and description from add-task message."""
        # Remove trigger words
        title = re.sub(
            r"^(add task|remind me to|remind me|schedule|add reminder|create task|new task)\s*",
            "", message, flags=re.IGNORECASE
        ).strip()

        # Extract date
        task_date = _today()
        date_patterns = [
            (r"\btoday\b", _today()),
            (r"\btomorrow\b", _tomorrow()),
            (r"\bon\s+(\d{4}-\d{2}-\d{2})\b", None),
            (r"\bon\s+(\d{2}/\d{2}/\d{4})\b", None),
            (r"\bfor\s+(\d{4}-\d{2}-\d{2})\b", None),
        ]
        for pattern, fixed_date in date_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                if fixed_date:
                    task_date = fixed_date
                else:
                    raw = match.group(1)
                    try:
                        if "/" in raw:
                            d, m, y = raw.split("/")
                            task_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                        else:
                            task_date = raw
                    except Exception:
                        task_date = _today()
                # Remove date phrase from title
                title = re.sub(r"\s*(today|tomorrow|on\s+\S+|for\s+\S+)\b", "", title, flags=re.IGNORECASE).strip()
                break

        # Check for day names
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(day_names):
            if re.search(rf"\b{day}\b", title, re.IGNORECASE):
                task_date = self._next_weekday(i)
                title = re.sub(rf"\b(on\s+)?{day}\b", "", title, flags=re.IGNORECASE).strip()
                break

        return title.strip(), task_date, ""

    def _extract_remove_title(self, message: str) -> str:
        title = re.sub(
            r"^(remove task|delete task|cancel reminder|remove reminder|delete reminder)\s*",
            "", message, flags=re.IGNORECASE
        ).strip()
        return title

    def _next_weekday(self, weekday: int) -> str:
        """Return the date of the next occurrence of the given weekday (0=Monday)."""
        today = date.today()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).isoformat()

    def _format_task_list(self, tasks: list[Task], label: str) -> str:
        if not tasks:
            return f"No tasks {label}."
        lines = [f"• {t.title} ({t.date})" + (f" — {t.description}" if t.description else "")
                 for t in tasks]
        return f"Tasks {label}:\n" + "\n".join(lines)

    def _format_reminders(self, tasks: list[Task]) -> str:
        if not tasks:
            return "No upcoming reminders for today or tomorrow."
        today_tasks = [t for t in tasks if t.date == _today()]
        tomorrow_tasks = [t for t in tasks if t.date == _tomorrow()]
        parts = []
        if today_tasks:
            parts.append("**Today:**\n" + "\n".join(f"• {t.title}" for t in today_tasks))
        if tomorrow_tasks:
            parts.append("**Tomorrow:**\n" + "\n".join(f"• {t.title}" for t in tomorrow_tasks))
        return "\n\n".join(parts)
