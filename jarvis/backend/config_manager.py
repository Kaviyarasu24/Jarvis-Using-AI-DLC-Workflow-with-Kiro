"""
ConfigManager — loads config.json and provides typed access to all settings.
Environment variables override config.json values (prefix: JARVIS_).
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULTS = {
    "ollama_model": "llama3.2:3b",
    "ollama_base_url": "http://localhost:11434",
    "stats_interval_seconds": 5,
    "battery_interval_seconds": 10,
    "cpu_alert_threshold": 90.0,
    "history_context_window": 20,
    "backend_port": 8000,
    "data_dir": "./data",
    "voice_timeout_seconds": 5,
    "voice_phrase_limit_seconds": 10,
    "tts_rate": 175,
}

_ENV_MAP = {
    "JARVIS_OLLAMA_MODEL": "ollama_model",
    "JARVIS_OLLAMA_BASE_URL": "ollama_base_url",
    "JARVIS_STATS_INTERVAL": "stats_interval_seconds",
    "JARVIS_BATTERY_INTERVAL": "battery_interval_seconds",
    "JARVIS_CPU_ALERT_THRESHOLD": "cpu_alert_threshold",
    "JARVIS_HISTORY_WINDOW": "history_context_window",
    "JARVIS_PORT": "backend_port",
    "JARVIS_DATA_DIR": "data_dir",
    "JARVIS_VOICE_TIMEOUT": "voice_timeout_seconds",
    "JARVIS_VOICE_PHRASE_LIMIT": "voice_phrase_limit_seconds",
    "JARVIS_TTS_RATE": "tts_rate",
}


class ConfigManager:
    """Loads and provides typed access to application configuration."""

    def __init__(self, config_path: str = "config.json") -> None:
        self._config: dict = dict(_DEFAULTS)
        self._config_path = config_path
        self.load()

    def load(self) -> None:
        """Load config from file, then apply environment variable overrides."""
        path = Path(self._config_path)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                self._config.update(file_config)
                logger.info(f"Config loaded from {path}")
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load config.json: {e}. Using defaults.")
        else:
            logger.warning(f"config.json not found at {path}. Using defaults.")

        # Apply environment variable overrides
        for env_key, config_key in _ENV_MAP.items():
            env_val = os.environ.get(env_key)
            if env_val is not None:
                self._config[config_key] = self._coerce(config_key, env_val)
                logger.info(f"Config override from env: {config_key}={env_val}")

    def _coerce(self, key: str, value: str):
        """Coerce string env var to the correct type based on default."""
        default = _DEFAULTS.get(key)
        if isinstance(default, int):
            return int(value)
        if isinstance(default, float):
            return float(value)
        return value

    def _get(self, key: str):
        return self._config.get(key, _DEFAULTS.get(key))

    @property
    def ollama_model(self) -> str:
        return str(self._get("ollama_model"))

    @property
    def ollama_base_url(self) -> str:
        return str(self._get("ollama_base_url"))

    @property
    def stats_interval_seconds(self) -> int:
        return int(self._get("stats_interval_seconds"))

    @property
    def battery_interval_seconds(self) -> int:
        return int(self._get("battery_interval_seconds"))

    @property
    def cpu_alert_threshold(self) -> float:
        return float(self._get("cpu_alert_threshold"))

    @property
    def history_context_window(self) -> int:
        return int(self._get("history_context_window"))

    @property
    def backend_port(self) -> int:
        return int(self._get("backend_port"))

    @property
    def data_dir(self) -> str:
        return str(self._get("data_dir"))

    @property
    def voice_timeout_seconds(self) -> int:
        return int(self._get("voice_timeout_seconds"))

    @property
    def voice_phrase_limit_seconds(self) -> int:
        return int(self._get("voice_phrase_limit_seconds"))

    @property
    def tts_rate(self) -> int:
        return int(self._get("tts_rate"))
