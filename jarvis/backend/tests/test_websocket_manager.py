"""Unit tests for WebSocketManager."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.websocket_manager import WebSocketManager, make_message


class TestMakeMessage:
    def test_returns_valid_json(self):
        result = make_message("test_type", {"key": "value"})
        parsed = json.loads(result)
        assert parsed["type"] == "test_type"
        assert parsed["payload"] == {"key": "value"}
        assert "timestamp" in parsed

    def test_timestamp_is_iso_format(self):
        result = make_message("ping", {})
        parsed = json.loads(result)
        # Should be parseable as ISO datetime
        from datetime import datetime
        datetime.fromisoformat(parsed["timestamp"].replace("Z", "+00:00"))

    def test_handles_none_payload(self):
        result = make_message("empty", None)
        parsed = json.loads(result)
        assert parsed["payload"] is None


class TestWebSocketManager:
    @pytest.fixture
    def manager(self):
        return WebSocketManager()

    @pytest.fixture
    def mock_ws(self):
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock(return_value='{"type":"user_message","payload":{"text":"hello"}}')
        ws.close = AsyncMock()
        return ws

    @pytest.mark.asyncio
    async def test_connect_accepts_websocket(self, manager, mock_ws):
        await manager.connect(mock_ws)
        mock_ws.accept.assert_called_once()
        assert manager.is_connected

    @pytest.mark.asyncio
    async def test_disconnect_clears_connection(self, manager, mock_ws):
        await manager.connect(mock_ws)
        await manager.disconnect(mock_ws)
        assert not manager.is_connected

    @pytest.mark.asyncio
    async def test_send_calls_send_text(self, manager, mock_ws):
        await manager.connect(mock_ws)
        await manager.send("chat_response", {"text": "hello"})
        mock_ws.send_text.assert_called_once()
        sent = json.loads(mock_ws.send_text.call_args[0][0])
        assert sent["type"] == "chat_response"
        assert sent["payload"]["text"] == "hello"

    @pytest.mark.asyncio
    async def test_send_silently_skips_when_not_connected(self, manager):
        # Should not raise even with no connection
        await manager.send("test", {})

    @pytest.mark.asyncio
    async def test_receive_parses_json(self, manager, mock_ws):
        await manager.connect(mock_ws)
        result = await manager.receive(mock_ws)
        assert result["type"] == "user_message"
        assert result["payload"]["text"] == "hello"

    @pytest.mark.asyncio
    async def test_receive_handles_malformed_json(self, manager, mock_ws):
        mock_ws.receive_text = AsyncMock(return_value="not json {{{")
        await manager.connect(mock_ws)
        result = await manager.receive(mock_ws)
        assert result["type"] == "__invalid__"

    @pytest.mark.asyncio
    async def test_second_connect_closes_previous(self, manager, mock_ws):
        ws2 = AsyncMock()
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        await manager.connect(mock_ws)
        await manager.connect(ws2)
        mock_ws.close.assert_called_once()
        assert manager.is_connected
