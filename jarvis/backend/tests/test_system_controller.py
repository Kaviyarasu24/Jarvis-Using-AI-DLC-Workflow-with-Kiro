"""Unit tests for SystemController."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from backend.system_controller import SystemController, ActionResult
from backend.config_manager import ConfigManager


@pytest.fixture
def config(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"data_dir": str(tmp_path)}))
    return ConfigManager(config_path=str(p))


@pytest.fixture
def controller(config):
    return SystemController(config)


class TestOpenUrl:
    @pytest.mark.asyncio
    async def test_open_url_success(self, controller):
        with patch("webbrowser.open", return_value=True):
            result = await controller.open_url("https://example.com")
        assert result.success
        assert "example.com" in result.output

    @pytest.mark.asyncio
    async def test_open_url_failure(self, controller):
        with patch("webbrowser.open", side_effect=Exception("no browser")):
            result = await controller.open_url("https://example.com")
        assert not result.success


class TestFileOperations:
    @pytest.mark.asyncio
    async def test_list_directory(self, controller, tmp_path):
        (tmp_path / "file.txt").write_text("hello")
        (tmp_path / "subdir").mkdir()
        result = await controller.list_directory(str(tmp_path))
        assert result.success
        assert "file.txt" in result.output
        assert "subdir" in result.output

    @pytest.mark.asyncio
    async def test_list_nonexistent_directory(self, controller):
        result = await controller.list_directory("/nonexistent/path/xyz")
        assert not result.success
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_read_file(self, controller, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = await controller.read_file(str(f))
        assert result.success
        assert "hello world" in result.output

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, controller):
        result = await controller.read_file("/nonexistent/file.txt")
        assert not result.success

    @pytest.mark.asyncio
    async def test_copy_file(self, controller, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("content")
        dst = tmp_path / "dst.txt"
        result = await controller.copy_file(str(src), str(dst))
        assert result.success
        assert dst.exists()

    @pytest.mark.asyncio
    async def test_move_file(self, controller, tmp_path):
        src = tmp_path / "src.txt"
        src.write_text("content")
        dst = tmp_path / "dst.txt"
        result = await controller.move_file(str(src), str(dst))
        assert result.success
        assert not src.exists()
        assert dst.exists()


class TestDestructiveOperations:
    @pytest.mark.asyncio
    async def test_delete_requires_confirmation(self, controller, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data")
        result = await controller.delete_file(str(f))
        assert result.requires_confirmation
        assert result.action_id is not None
        assert f.exists()  # not deleted yet

    @pytest.mark.asyncio
    async def test_delete_confirmed(self, controller, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("data")
        # First call — get action_id
        pending = await controller.delete_file(str(f))
        # Confirm
        result = await controller.confirm_action(pending.action_id)
        assert "Deleted" in result["text"] or result.get("text")
        assert not f.exists()

    @pytest.mark.asyncio
    async def test_run_command_requires_confirmation(self, controller):
        result = await controller.run_command("echo hello")
        assert result.requires_confirmation

    @pytest.mark.asyncio
    async def test_run_command_confirmed(self, controller):
        pending = await controller.run_command("echo hello_test")
        result = await controller.confirm_action(pending.action_id)
        assert "hello_test" in result.get("text", "")

    @pytest.mark.asyncio
    async def test_confirm_expired_action(self, controller):
        result = await controller.confirm_action("nonexistent-id")
        assert "expired" in result["text"].lower() or "not found" in result["text"].lower()


class TestSystemMonitorAlerts:
    def test_battery_connected_alert(self):
        from backend.system_monitor import SystemMonitor, BatterySnapshot
        from backend.config_manager import ConfigManager
        from unittest.mock import MagicMock
        import json, tempfile, os

        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = os.path.join(tmp, "config.json")
            with open(cfg_path, "w") as f:
                json.dump({"cpu_alert_threshold": 90.0, "battery_interval_seconds": 10, "stats_interval_seconds": 5}, f)
            config = ConfigManager(config_path=cfg_path)
            ws = MagicMock()
            monitor = SystemMonitor(config, ws)

            # Simulate transition: not charging → charging
            monitor._prev_battery = BatterySnapshot(level=50.0, charging=False)
            stats = {"battery_level": 50.0, "battery_charging": True}
            alerts = monitor._check_battery_alerts(stats)
            assert any(a.type == "battery_connected" for a in alerts)

    def test_battery_low_alert(self):
        from backend.system_monitor import SystemMonitor, BatterySnapshot
        from backend.config_manager import ConfigManager
        from unittest.mock import MagicMock
        import json, tempfile, os

        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = os.path.join(tmp, "config.json")
            with open(cfg_path, "w") as f:
                json.dump({"cpu_alert_threshold": 90.0, "battery_interval_seconds": 10, "stats_interval_seconds": 5}, f)
            config = ConfigManager(config_path=cfg_path)
            ws = MagicMock()
            monitor = SystemMonitor(config, ws)

            monitor._prev_battery = BatterySnapshot(level=35.0, charging=False)
            stats = {"battery_level": 25.0, "battery_charging": False}
            alerts = monitor._check_battery_alerts(stats)
            assert any(a.type == "battery_low" for a in alerts)

    def test_wifi_disconnected_alert(self):
        from backend.system_monitor import SystemMonitor
        from backend.config_manager import ConfigManager
        from unittest.mock import MagicMock
        import json, tempfile, os

        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = os.path.join(tmp, "config.json")
            with open(cfg_path, "w") as f:
                json.dump({"cpu_alert_threshold": 90.0, "battery_interval_seconds": 10, "stats_interval_seconds": 5}, f)
            config = ConfigManager(config_path=cfg_path)
            ws = MagicMock()
            monitor = SystemMonitor(config, ws)

            monitor._prev_network = True
            alerts = monitor._check_network_alerts({"network_connected": False})
            assert any(a.type == "wifi_disconnected" for a in alerts)
