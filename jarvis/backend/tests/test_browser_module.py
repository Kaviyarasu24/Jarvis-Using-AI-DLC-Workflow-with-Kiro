"""Unit tests for BrowserModule."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.browser_module import BrowserModule, BrowserResult, SearchIntent
from backend.config_manager import ConfigManager


@pytest.fixture
def config(tmp_path):
    p = tmp_path / "config.json"
    p.write_text(json.dumps({
        "ollama_model": "llama3.2:3b",
        "ollama_base_url": "http://localhost:11434",
        "data_dir": str(tmp_path),
    }))
    return ConfigManager(config_path=str(p))


@pytest.fixture
def mock_ai_core():
    core = AsyncMock()
    core.chat = AsyncMock(return_value="Summarized result about Python async.")
    return core


@pytest.fixture
def browser_module_no_browser(config, mock_ai_core):
    """BrowserModule with browser-use unavailable."""
    with patch.object(BrowserModule, "_check_browser_use", return_value=False):
        return BrowserModule(config=config, ai_core=mock_ai_core)


class TestQueryExtraction:
    def test_extract_search_for(self, browser_module_no_browser):
        intent = browser_module_no_browser._extract_query("search for Python tutorials")
        assert intent.query == "Python tutorials"

    def test_extract_what_is(self, browser_module_no_browser):
        intent = browser_module_no_browser._extract_query("what is machine learning?")
        assert "machine learning" in intent.query

    def test_extract_how_to(self, browser_module_no_browser):
        intent = browser_module_no_browser._extract_query("how to install Docker")
        assert "install Docker" in intent.query

    def test_extract_find(self, browser_module_no_browser):
        intent = browser_module_no_browser._extract_query("find information about FastAPI")
        assert "FastAPI" in intent.query

    def test_extract_direct_url(self, browser_module_no_browser):
        intent = browser_module_no_browser._extract_query("https://example.com")
        assert intent.query == "https://example.com"

    def test_extract_fallback(self, browser_module_no_browser):
        intent = browser_module_no_browser._extract_query("latest news today")
        assert intent.query == "latest news today"


class TestSearchWithoutBrowser:
    @pytest.mark.asyncio
    async def test_returns_error_when_browser_unavailable(self, browser_module_no_browser):
        result = await browser_module_no_browser.search("test query")
        assert not result.success
        assert "not available" in result.error.lower() or "install" in result.error.lower()

    @pytest.mark.asyncio
    async def test_handle_returns_error_dict(self, browser_module_no_browser):
        result = await browser_module_no_browser.handle("search for something")
        assert "text" in result
        assert "message_type" in result


class TestBrowserResult:
    def test_browser_result_defaults(self):
        r = BrowserResult(success=True, query="test", summary="summary")
        assert r.sources == []
        assert r.error is None

    def test_browser_result_with_sources(self):
        r = BrowserResult(
            success=True,
            query="test",
            summary="found it",
            sources=["https://example.com"],
        )
        assert len(r.sources) == 1
