"""Unit tests for CalendarManager."""

import json
import pytest
from datetime import date, timedelta

from backend.calendar_manager import CalendarManager, Task
from backend.config_manager import ConfigManager


@pytest.fixture
def config(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"data_dir": str(tmp_path)}))
    return ConfigManager(config_path=str(p))


@pytest.fixture
def manager(config):
    return CalendarManager(config)


today = date.today().isoformat()
tomorrow = (date.today() + timedelta(days=1)).isoformat()


class TestTaskCRUD:
    def test_add_task(self, manager):
        task = manager.add_task("Buy groceries", today)
        assert task.title == "Buy groceries"
        assert task.date == today
        assert task.id is not None

    def test_add_task_persists(self, config):
        m1 = CalendarManager(config)
        m1.add_task("Persistent task", today)
        m2 = CalendarManager(config)
        assert any(t.title == "Persistent task" for t in m2.get_all_tasks())

    def test_remove_task_by_id(self, manager):
        task = manager.add_task("Remove me", today)
        removed = manager.remove_task(task_id=task.id)
        assert removed
        assert manager.get_task_by_id(task.id) is None

    def test_remove_task_by_title(self, manager):
        manager.add_task("Delete by title", today)
        removed = manager.remove_task(title="Delete by title")
        assert removed
        assert not any(t.title == "Delete by title" for t in manager.get_all_tasks())

    def test_remove_nonexistent_task(self, manager):
        removed = manager.remove_task(task_id="nonexistent-id")
        assert not removed

    def test_get_today_tasks(self, manager):
        manager.add_task("Today task", today)
        manager.add_task("Tomorrow task", tomorrow)
        today_tasks = manager.get_today_tasks()
        assert all(t.date == today for t in today_tasks)
        assert any(t.title == "Today task" for t in today_tasks)

    def test_get_tomorrow_tasks(self, manager):
        manager.add_task("Tomorrow task", tomorrow)
        tomorrow_tasks = manager.get_tomorrow_tasks()
        assert all(t.date == tomorrow for t in tomorrow_tasks)

    def test_get_reminders_includes_today_and_tomorrow(self, manager):
        manager.add_task("Today", today)
        manager.add_task("Tomorrow", tomorrow)
        reminders = manager.get_reminders()
        dates = {t.date for t in reminders}
        assert today in dates
        assert tomorrow in dates

    def test_corrupted_json_resets_to_empty(self, config, tmp_path):
        (tmp_path / "tasks.json").write_text("{ bad json }")
        m = CalendarManager(config)
        assert m.get_all_tasks() == []


class TestNLParsing:
    @pytest.mark.asyncio
    async def test_add_task_via_chat(self, manager):
        result = await manager.handle("add task Buy milk for today")
        assert "added" in result["text"].lower() or "Buy milk" in result["text"]

    @pytest.mark.asyncio
    async def test_view_today_tasks(self, manager):
        manager.add_task("Today task", today)
        result = await manager.handle("show today's tasks")
        assert "Today task" in result["text"] or "today" in result["text"].lower()

    @pytest.mark.asyncio
    async def test_remove_task_via_chat(self, manager):
        manager.add_task("Remove this", today)
        result = await manager.handle("remove task Remove this")
        assert "removed" in result["text"].lower() or "Remove this" in result["text"]

    @pytest.mark.asyncio
    async def test_reminders_via_chat(self, manager):
        manager.add_task("Reminder task", today)
        result = await manager.handle("what are my reminders?")
        assert "text" in result

    @pytest.mark.asyncio
    async def test_add_task_no_title_returns_help(self, manager):
        result = await manager.handle("add task")
        assert "title" in result["text"].lower() or "provide" in result["text"].lower()


class TestDateParsing:
    def test_extract_today(self, manager):
        title, task_date, _ = manager._extract_task_details("add task Meeting today")
        assert task_date == today

    def test_extract_tomorrow(self, manager):
        title, task_date, _ = manager._extract_task_details("add task Call doctor tomorrow")
        assert task_date == tomorrow

    def test_extract_iso_date(self, manager):
        title, task_date, _ = manager._extract_task_details("add task Event on 2026-12-25")
        assert task_date == "2026-12-25"
