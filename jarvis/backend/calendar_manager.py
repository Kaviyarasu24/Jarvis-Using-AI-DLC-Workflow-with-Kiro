"""
CalendarManager — JSON-based local task/calendar management.
Supports CRUD, natural language parsing, time-based reminders via WebSocket.
"""

import asyncio
import json
import logging
import re
import uuid
from dataclasses import dataclass, asdict, field
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
    time: str           # "HH:MM" or "" for all-day
    description: str
    completed: bool
    created_at: str     # ISO 8601


def _today() -> str:
    return date.today().isoformat()


def _tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_local() -> datetime:
    return datetime.now()


class CalendarManager:
    """Manages local JSON-based tasks with NL command parsing and timed reminders."""

    def __init__(self, config: ConfigManager, ws_manager=None) -> None:
        self._config = config
        self._ws = ws_manager
        self._tasks: list[Task] = []
        self._tasks_path = Path(config.data_dir) / "tasks.json"
        self._reminder_task: Optional[asyncio.Task] = None
        self._fired_reminders: set[str] = set()  # task IDs already alerted
        self.load_tasks()

    # ------------------------------------------------------------------
    # Reminder loop
    # ------------------------------------------------------------------

    async def start_reminder_loop(self) -> None:
        """Start background loop that fires WebSocket alerts at task time."""
        if self._reminder_task and not self._reminder_task.done():
            return
        self._reminder_task = asyncio.create_task(self._reminder_loop())
        logger.info("Reminder loop started.")

    async def stop_reminder_loop(self) -> None:
        if self._reminder_task and not self._reminder_task.done():
            self._reminder_task.cancel()

    async def _reminder_loop(self) -> None:
        while True:
            await asyncio.sleep(30)  # check every 30 seconds
            if not self._ws:
                continue
            now = _now_local()
            today_str = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M")

            for task in self._tasks:
                if task.completed:
                    continue
                if task.id in self._fired_reminders:
                    continue
                if task.date != today_str:
                    continue
                if not task.time:
                    continue
                if task.time == current_time:
                    self._fired_reminders.add(task.id)
                    await self._ws.broadcast("alert", {
                        "id": str(uuid.uuid4()),
                        "type": "task_reminder",
                        "message": f"⏰ Reminder: {task.title}",
                        "severity": "info",
                        "timestamp": _now_iso(),
                    })
                    logger.info(f"Reminder fired for task: {task.title!r}")

    # ------------------------------------------------------------------
    # Public: NL command handler
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        intent = self._parse_intent(message)

        if intent["action"] == "add":
            title = intent.get("title", "").strip()
            if not title:
                return {"text": "Please provide a task title. Example: 'add task Buy groceries for tomorrow at 3pm'", "message_type": "text"}
            task_date = intent.get("date") or _today()
            task_time = intent.get("time", "")
            description = intent.get("description", "")
            task = self.add_task(title, task_date, task_time, description)
            time_str = f" at {task.time}" if task.time else ""
            return {"text": f"✅ Task added: **{task.title}** on {task.date}{time_str}", "message_type": "text"}

        elif intent["action"] == "complete":
            title = intent.get("title", "").strip()
            done = self.complete_task(title=title)
            if done:
                return {"text": f"✅ Marked complete: {title}", "message_type": "text"}
            return {"text": f"No task found: '{title}'", "message_type": "text"}

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

        return {"text": "Try: 'add task X for tomorrow at 3pm', 'show today's tasks', 'remove task X'", "message_type": "text"}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_task(self, title: str, task_date: str, task_time: str = "", description: str = "") -> Task:
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            date=task_date,
            time=task_time,
            description=description,
            completed=False,
            created_at=_now_iso(),
        )
        self._tasks.append(task)
        self.save_tasks()
        logger.info(f"Task added: {title!r} on {task_date} {task_time}")
        return task

    def complete_task(self, task_id: Optional[str] = None, title: Optional[str] = None) -> bool:
        for t in self._tasks:
            if (task_id and t.id == task_id) or (title and t.title.lower() == title.lower()):
                t.completed = True
                self.save_tasks()
                return True
        return False

    def remove_task(self, task_id: Optional[str] = None, title: Optional[str] = None) -> bool:
        original_len = len(self._tasks)
        if task_id:
            self._tasks = [t for t in self._tasks if t.id != task_id]
        elif title:
            self._tasks = [t for t in self._tasks if t.title.lower() != title.lower()]
        if len(self._tasks) < original_len:
            self.save_tasks()
            return True
        return False

    def get_all_tasks(self) -> list[Task]:
        return sorted(self._tasks, key=lambda t: (t.date, t.time or "99:99"))

    def get_tasks_for_date(self, task_date: str) -> list[Task]:
        return sorted(
            [t for t in self._tasks if t.date == task_date],
            key=lambda t: t.time or "99:99",
        )

    def get_today_tasks(self) -> list[Task]:
        return self.get_tasks_for_date(_today())

    def get_tomorrow_tasks(self) -> list[Task]:
        return self.get_tasks_for_date(_tomorrow())

    def get_reminders(self) -> list[Task]:
        return [t for t in self.get_today_tasks() + self.get_tomorrow_tasks() if not t.completed]

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
                raw_tasks = data.get("tasks", [])
                self._tasks = []
                for t in raw_tasks:
                    # Migrate old tasks that lack time/completed fields
                    t.setdefault("time", "")
                    t.setdefault("completed", False)
                    self._tasks.append(Task(**t))
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
    # NL parsing
    # ------------------------------------------------------------------

    def _parse_intent(self, message: str) -> dict:
        msg_lower = message.lower()

        if any(t in msg_lower for t in ["add task", "remind me", "schedule", "add reminder", "create task", "new task"]):
            title, task_date, task_time, description = self._extract_task_details(message)
            return {"action": "add", "title": title, "date": task_date, "time": task_time, "description": description}

        if any(t in msg_lower for t in ["complete task", "mark done", "finish task", "done with"]):
            title = re.sub(r"^(complete task|mark done|finish task|done with)\s*", "", message, flags=re.IGNORECASE).strip()
            return {"action": "complete", "title": title}

        if any(t in msg_lower for t in ["remove task", "delete task", "cancel reminder", "remove reminder"]):
            title = re.sub(r"^(remove task|delete task|cancel reminder|remove reminder)\s*", "", message, flags=re.IGNORECASE).strip()
            return {"action": "remove", "title": title}

        if any(t in msg_lower for t in ["today's task", "today task", "tasks today", "schedule today"]):
            return {"action": "view", "date": "today"}

        if "tomorrow" in msg_lower and any(t in msg_lower for t in ["task", "schedule", "reminder"]):
            return {"action": "view", "date": "tomorrow"}

        if any(t in msg_lower for t in ["reminder", "coming up", "upcoming", "what's due"]):
            return {"action": "reminders"}

        if any(t in msg_lower for t in ["show task", "list task", "my schedule", "view task", "all task"]):
            return {"action": "view", "date": "all"}

        return {"action": "view", "date": "all"}

    def _extract_task_details(self, message: str) -> tuple[str, str, str, str]:
        title = re.sub(
            r"^(add task|remind me to|remind me|schedule|add reminder|create task|new task)\s*",
            "", message, flags=re.IGNORECASE,
        ).strip()

        task_date = _today()
        task_time = ""

        # Extract time first (before stripping date words)
        time_match = re.search(
            r'\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',
            title, re.IGNORECASE,
        )
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            meridiem = (time_match.group(3) or "").lower()
            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
            task_time = f"{hour:02d}:{minute:02d}"
            title = title[:time_match.start()].strip() + " " + title[time_match.end():].strip()
            title = title.strip()

        # Extract date
        date_patterns = [
            (r"\btoday\b", _today()),
            (r"\btomorrow\b", _tomorrow()),
            (r"\bon\s+(\d{4}-\d{2}-\d{2})\b", None),
            (r"\bfor\s+(\d{4}-\d{2}-\d{2})\b", None),
            (r"\bon\s+(\d{2}/\d{2}/\d{4})\b", None),
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
                title = re.sub(r"\s*(today|tomorrow|on\s+\S+|for\s+\S+)\b", "", title, flags=re.IGNORECASE).strip()
                break

        # Day names
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(day_names):
            if re.search(rf"\b{day}\b", title, re.IGNORECASE):
                task_date = self._next_weekday(i)
                title = re.sub(rf"\b(on\s+)?{day}\b", "", title, flags=re.IGNORECASE).strip()
                break

        return title.strip(), task_date, task_time, ""

    def _next_weekday(self, weekday: int) -> str:
        today = date.today()
        days_ahead = weekday - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).isoformat()

    def _format_task_list(self, tasks: list[Task], label: str) -> str:
        if not tasks:
            return f"No tasks {label}."
        lines = []
        for t in tasks:
            status = "✅" if t.completed else "•"
            time_str = f" {t.time}" if t.time else ""
            desc_str = f" — {t.description}" if t.description else ""
            lines.append(f"{status} {t.title} ({t.date}{time_str}){desc_str}")
        return f"Tasks {label}:\n" + "\n".join(lines)

    def _format_reminders(self, tasks: list[Task]) -> str:
        if not tasks:
            return "No upcoming reminders for today or tomorrow."
        today_tasks = [t for t in tasks if t.date == _today()]
        tomorrow_tasks = [t for t in tasks if t.date == _tomorrow()]
        parts = []
        if today_tasks:
            parts.append("**Today:**\n" + "\n".join(
                f"• {t.title}" + (f" at {t.time}" if t.time else "") for t in today_tasks
            ))
        if tomorrow_tasks:
            parts.append("**Tomorrow:**\n" + "\n".join(
                f"• {t.title}" + (f" at {t.time}" if t.time else "") for t in tomorrow_tasks
            ))
        return "\n\n".join(parts)
