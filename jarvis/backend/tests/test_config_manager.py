"""Unit tests for ConfigManager."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from backend.config_manager import ConfigManager


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config.json for testing."""
    cfg = {
        "ollama_model": "test-model",
        "ollama_base_url": "http://test:11434",
        "stats_interval_seconds": 10,
        "battery_interval_seconds": 20,
        "cpu_alert_threshold": 80.0,
        "history_context_window": 10,
        "backend_port": 9000,
        "data_dir": "./test_data",
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(cfg))
    return str(config_path)


class TestConfigManagerDefaults:
    def test_uses_defaults_when_no_file(self, tmp_path):
        cm = ConfigManager(config_path=str(tmp_path / "nonexistent.json"))
        assert cm.ollama_model == "llama3.2:3b"
        assert cm.ollama_base_url == "http://localhost:11434"
        assert cm.stats_interval_seconds == 5
        assert cm.battery_interval_seconds == 10
        assert cm.cpu_alert_threshold == 90.0
        assert cm.history_context_window == 20
        assert cm.backend_port == 8000
        assert cm.data_dir == "./data"

    def test_loads_from_file(self, config_file):
        cm = ConfigManager(config_path=config_file)
        assert cm.ollama_model == "test-model"
        assert cm.ollama_base_url == "http://test:11434"
        assert cm.stats_interval_seconds == 10
        assert cm.backend_port == 9000

    def test_partial_config_uses_defaults_for_missing_keys(self, tmp_path):
        partial = {"ollama_model": "partial-model"}
        path = tmp_path / "partial.json"
        path.write_text(json.dumps(partial))
        cm = ConfigManager(config_path=str(path))
        assert cm.ollama_model == "partial-model"
        assert cm.backend_port == 8000  # default

    def test_malformed_json_uses_defaults(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{ not valid json }")
        cm = ConfigManager(config_path=str(path))
        assert cm.ollama_model == "llama3.2:3b"


class TestConfigManagerEnvOverrides:
    def test_env_var_overrides_model(self, config_file, monkeypatch):
        monkeypatch.setenv("JARVIS_OLLAMA_MODEL", "env-model")
        cm = ConfigManager(config_path=config_file)
        assert cm.ollama_model == "env-model"

    def test_env_var_overrides_port(self, config_file, monkeypatch):
        monkeypatch.setenv("JARVIS_PORT", "7777")
        cm = ConfigManager(config_path=config_file)
        assert cm.backend_port == 7777

    def test_env_var_overrides_float(self, config_file, monkeypatch):
        monkeypatch.setenv("JARVIS_CPU_ALERT_THRESHOLD", "75.5")
        cm = ConfigManager(config_path=config_file)
        assert cm.cpu_alert_threshold == 75.5


class TestConfigManagerTypes:
    def test_stats_interval_is_int(self, config_file):
        cm = ConfigManager(config_path=config_file)
        assert isinstance(cm.stats_interval_seconds, int)

    def test_cpu_threshold_is_float(self, config_file):
        cm = ConfigManager(config_path=config_file)
        assert isinstance(cm.cpu_alert_threshold, float)

    def test_port_is_int(self, config_file):
        cm = ConfigManager(config_path=config_file)
        assert isinstance(cm.backend_port, int)
