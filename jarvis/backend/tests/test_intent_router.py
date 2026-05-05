"""Unit tests for IntentRouter."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.intent_router import IntentRouter
from backend.ai_core import AICore
from backend.websocket_manager import WebSocketManager


@pytest.fixture
def mock_ai_core():
    core = AsyncMock(spec=AICore)
    core.classify_intent = AsyncMock(return_value="chat")
    core.chat = AsyncMock(return_value="Hello from AI")
    return core


@pytest.fixture
def mock_ws():
    ws = MagicMock(spec=WebSocketManager)
    ws.send = AsyncMock()
    return ws


@pytest.fixture
def router(mock_ai_core, mock_ws):
    return IntentRouter(ai_core=mock_ai_core, ws_manager=mock_ws)


class TestIntentRouter:
    @pytest.mark.asyncio
    async def test_routes_to_registered_handler(self, router, mock_ai_core):
        mock_ai_core.classify_intent.return_value = "chat"
        handler = AsyncMock(return_value={"text": "handled", "message_type": "text"})
        router.register_handler("chat", handler)

        result = await router.route("hello")
        handler.assert_called_once_with("hello")
        assert result["text"] == "handled"

    @pytest.mark.asyncio
    async def test_falls_back_to_chat_for_unregistered_intent(self, router, mock_ai_core):
        mock_ai_core.classify_intent.return_value = "search"
        chat_handler = AsyncMock(return_value={"text": "chat fallback", "message_type": "text"})
        router.register_handler("chat", chat_handler)

        result = await router.route("search for something")
        chat_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_exception_returns_error_message(self, router, mock_ai_core):
        mock_ai_core.classify_intent.return_value = "chat"
        bad_handler = AsyncMock(side_effect=Exception("handler crashed"))
        router.register_handler("chat", bad_handler)

        result = await router.route("test")
        assert "message_type" in result

    @pytest.mark.asyncio
    async def test_register_multiple_handlers(self, router):
        h1 = AsyncMock(return_value={"text": "code response", "message_type": "code"})
        h2 = AsyncMock(return_value={"text": "system response", "message_type": "text"})
        router.register_handler("code", h1)
        router.register_handler("system", h2)
        assert "code" in router._handlers
        assert "system" in router._handlers
