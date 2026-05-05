"""Unit tests for AICore."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend.ai_core import AICore, OllamaUnavailableError, OllamaTimeoutError
from backend.config_manager import ConfigManager


@pytest.fixture
def config(tmp_path):
    cfg = {
        "ollama_model": "test-model",
        "ollama_base_url": "http://localhost:11434",
        "history_context_window": 5,
        "data_dir": str(tmp_path),
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    return ConfigManager(config_path=str(p))


@pytest.fixture
def mock_http_client():
    client = AsyncMock(spec=httpx.AsyncClient)
    response = MagicMock()
    response.status_code = 200
    response.raise_for_status = MagicMock()
    response.json = MagicMock(return_value={
        "message": {"role": "assistant", "content": "Hello! How can I help?"},
        "done": True,
    })
    client.post = AsyncMock(return_value=response)
    return client


@pytest.fixture
def ai_core(config, mock_http_client):
    return AICore(config=config, http_client=mock_http_client)


class TestConversationHistory:
    def test_starts_with_empty_history(self, ai_core):
        assert ai_core.get_context_window(10) == []

    def test_append_and_retrieve(self, ai_core):
        ai_core.append_to_history("user", "hello")
        ai_core.append_to_history("assistant", "hi there")
        ctx = ai_core.get_context_window(10)
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"
        assert ctx[1]["role"] == "assistant"

    def test_context_window_truncates(self, ai_core):
        for i in range(10):
            ai_core.append_to_history("user", f"msg {i}")
        ctx = ai_core.get_context_window(3)
        assert len(ctx) == 3
        assert ctx[-1]["content"] == "msg 9"

    def test_clear_history(self, ai_core):
        ai_core.append_to_history("user", "test")
        ai_core.clear_history()
        assert ai_core.get_context_window(10) == []

    def test_save_and_load_history(self, config, mock_http_client, tmp_path):
        core = AICore(config=config, http_client=mock_http_client)
        core.append_to_history("user", "persisted message")
        core.save_history()

        core2 = AICore(config=config, http_client=mock_http_client)
        ctx = core2.get_context_window(10)
        assert any(m["content"] == "persisted message" for m in ctx)

    def test_corrupted_history_resets_to_empty(self, config, mock_http_client, tmp_path):
        hist_path = tmp_path / "conversation_history.json"
        hist_path.write_text("{ not valid json }")
        core = AICore(config=config, http_client=mock_http_client)
        assert core.get_context_window(10) == []


class TestOllamaChat:
    @pytest.mark.asyncio
    async def test_chat_returns_response(self, ai_core):
        result = await ai_core.chat("Hello")
        assert result == "Hello! How can I help?"

    @pytest.mark.asyncio
    async def test_chat_appends_to_history(self, ai_core):
        await ai_core.chat("Hello")
        ctx = ai_core.get_context_window(10)
        assert any(m["role"] == "user" and m["content"] == "Hello" for m in ctx)
        assert any(m["role"] == "assistant" for m in ctx)

    @pytest.mark.asyncio
    async def test_chat_handles_ollama_unavailable(self, config, tmp_path):
        client = AsyncMock()
        client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        core = AICore(config=config, http_client=client)
        result = await core.chat("Hello")
        assert "Ollama" in result or "AI engine" in result

    @pytest.mark.asyncio
    async def test_chat_handles_timeout(self, config, tmp_path):
        client = AsyncMock()
        client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        core = AICore(config=config, http_client=client)
        result = await core.chat("Hello")
        assert "too long" in result or "again" in result


class TestIntentClassification:
    @pytest.mark.asyncio
    async def test_classify_returns_valid_intent(self, ai_core, mock_http_client):
        mock_http_client.post.return_value.json.return_value = {
            "message": {"role": "assistant", "content": "code"},
            "done": True,
        }
        intent = await ai_core.classify_intent("write a python function")
        assert intent == "code"

    @pytest.mark.asyncio
    async def test_classify_defaults_to_chat_on_unknown(self, ai_core, mock_http_client):
        mock_http_client.post.return_value.json.return_value = {
            "message": {"role": "assistant", "content": "unknown_intent"},
            "done": True,
        }
        intent = await ai_core.classify_intent("something weird")
        assert intent == "chat"

    @pytest.mark.asyncio
    async def test_classify_defaults_to_chat_on_error(self, config, tmp_path):
        client = AsyncMock()
        client.post = AsyncMock(side_effect=Exception("network error"))
        core = AICore(config=config, http_client=client)
        intent = await core.classify_intent("test")
        assert intent == "chat"
