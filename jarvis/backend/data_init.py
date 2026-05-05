"""
data_init — ensures the data directory and required JSON files exist on startup.
Creates them with empty structures if missing.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_INITIAL_STRUCTURES = {
    "conversation_history.json": {"messages": []},
    "tasks.json": {"tasks": []},
}


def initialize_data_directory(data_dir: str) -> None:
    """Create data directory and initialize JSON files if they don't exist."""
    path = Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Data directory ready: {path.resolve()}")

    for filename, initial_data in _INITIAL_STRUCTURES.items():
        file_path = path / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
            logger.info(f"Created {file_path}")
        else:
            logger.debug(f"Data file already exists: {file_path}")
