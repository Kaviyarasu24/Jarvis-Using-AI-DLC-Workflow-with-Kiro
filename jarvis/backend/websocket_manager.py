"""
WebSocketManager — manages the single active WebSocket connection.
Handles connect/disconnect lifecycle and message send/broadcast.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_message(msg_type: str, payload: Any) -> str:
    """Serialize a WebSocket message envelope to JSON string."""
    return json.dumps({
        "type": msg_type,
        "payload": payload,
        "timestamp": _now_iso(),
    })


class WebSocketManager:
    """Manages the single active WebSocket connection (single-user app)."""

    def __init__(self) -> None:
        self._connection: WebSocket | None = None

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection, replacing any existing one."""
        await websocket.accept()
        self._connection = websocket
        logger.info("WebSocket client connected.")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove the WebSocket connection on disconnect."""
        if self._connection is websocket:
            self._connection = None
        logger.info("WebSocket client disconnected.")

    @property
    def is_connected(self) -> bool:
        return self._connection is not None

    async def send(self, msg_type: str, payload: Any) -> None:
        """Send a message to the active connection. Silently skips if not connected."""
        if self._connection is None:
            logger.debug(f"No active connection; dropping message type={msg_type}")
            return
        try:
            await self._connection.send_text(make_message(msg_type, payload))
        except Exception as e:
            logger.warning(f"Failed to send WebSocket message: {e}")
            self._connection = None

    async def broadcast(self, msg_type: str, payload: Any) -> None:
        """Alias for send() — single-user app has only one connection."""
        await self.send(msg_type, payload)

    async def receive(self, websocket: WebSocket) -> dict:
        """Receive and parse an incoming WebSocket message. Returns parsed dict."""
        raw = await websocket.receive_text()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.warning(f"Malformed WebSocket message: {e}")
            return {"type": "__invalid__", "payload": {}}
