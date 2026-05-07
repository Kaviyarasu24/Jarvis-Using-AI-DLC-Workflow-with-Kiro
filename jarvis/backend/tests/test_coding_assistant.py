"""Unit tests for CodingAssistant."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.coding_assistant import CodingAssistant, CodeBlock


@pytest.fixture
def mock_ai_core():
    core = MagicMock()
    core._config = MagicMock()
    core._config.ollama_model = "llama3.2:3b"
    core._config.ollama_base_url = "http://127.0.0.1:11434"
    # _ollama_chat is used by the blocking path
    core._ollama_chat = AsyncMock(
        return_value="```python\nprint('hello')\n```\nThis prints hello."
    )
    # chat kept for backward compat
    core.chat = AsyncMock(
        return_value="```python\nprint('hello')\n```\nThis prints hello."
    )
    return core


@pytest.fixture
def assistant(mock_ai_core):
    # No ws_manager → uses blocking path (testable without WebSocket)
    return CodingAssistant(ai_core=mock_ai_core)


# ---------------------------------------------------------------------------
# Task type detection
# ---------------------------------------------------------------------------
class TestTaskTypeDetection:
    def test_detect_generate(self, assistant):
        assert assistant.detect_task_type("write a function to sort a list") == "generate"

    def test_detect_generate_create(self, assistant):
        assert assistant.detect_task_type("create a Python class for a bank account") == "generate"

    def test_detect_explain(self, assistant):
        assert assistant.detect_task_type("explain this code") == "explain"

    def test_detect_explain_what_does(self, assistant):
        assert assistant.detect_task_type("what does this function do?") == "explain"

    def test_detect_debug(self, assistant):
        assert assistant.detect_task_type("debug this error: TypeError") == "debug"

    def test_detect_debug_fix(self, assistant):
        assert assistant.detect_task_type("fix the bug in my code") == "debug"

    def test_detect_refactor(self, assistant):
        assert assistant.detect_task_type("refactor this function") == "refactor"

    def test_detect_review(self, assistant):
        assert assistant.detect_task_type("review my code") == "review"

    def test_default_to_generate(self, assistant):
        assert assistant.detect_task_type("something unrelated") == "generate"


# ---------------------------------------------------------------------------
# Code block extraction
# ---------------------------------------------------------------------------
class TestCodeBlockExtraction:
    def test_extract_python_block(self, assistant):
        text = "Here is the code:\n```python\nprint('hello')\n```\nDone."
        blocks = assistant._extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "print" in blocks[0].content

    def test_extract_multiple_blocks(self, assistant):
        text = "```python\nx = 1\n```\nAnd also:\n```javascript\nconsole.log(1)\n```"
        blocks = assistant._extract_code_blocks(text)
        assert len(blocks) == 2

    def test_extract_no_language(self, assistant):
        text = "```\nsome code\n```"
        blocks = assistant._extract_code_blocks(text)
        assert blocks[0].language == "text"

    def test_no_code_blocks(self, assistant):
        blocks = assistant._extract_code_blocks("Just plain text, no code.")
        assert blocks == []


# ---------------------------------------------------------------------------
# Language inference
# ---------------------------------------------------------------------------
class TestLanguageInference:
    def test_infer_python(self, assistant):
        assert assistant._infer_language("def foo():\n    return 1") == "python"

    def test_infer_javascript(self, assistant):
        assert assistant._infer_language("const x = () => console.log('hi')") == "javascript"

    def test_infer_java(self, assistant):
        assert assistant._infer_language("public class Foo { void main() {} }") == "java"

    def test_infer_unknown(self, assistant):
        assert assistant._infer_language("xyz abc 123") == "text"


# ---------------------------------------------------------------------------
# Handle (blocking path — no ws_manager)
# ---------------------------------------------------------------------------
class TestHandle:
    @pytest.mark.asyncio
    async def test_handle_returns_code_message_type(self, assistant):
        result = await assistant.handle("write a hello world in python")
        assert result["message_type"] == "code"
        assert result["language"] == "python"

    @pytest.mark.asyncio
    async def test_handle_returns_text_when_no_code_block(self, assistant, mock_ai_core):
        mock_ai_core._ollama_chat.return_value = "This is just an explanation with no code."
        result = await assistant.handle("explain recursion")
        assert result["message_type"] == "text"

    @pytest.mark.asyncio
    async def test_handle_uses_correct_system_prompt_for_debug(self, assistant, mock_ai_core):
        await assistant.handle("debug this error")
        call_kwargs = mock_ai_core._ollama_chat.call_args
        system = call_kwargs[1].get("system") or call_kwargs[0][1]
        assert "debug" in system.lower() or "bug" in system.lower()

    @pytest.mark.asyncio
    async def test_handle_does_not_call_chat_history(self, assistant, mock_ai_core):
        """Coding responses must not go through ai_core.chat() to avoid history pollution."""
        await assistant.handle("write a sort function")
        mock_ai_core.chat.assert_not_called()
        mock_ai_core._ollama_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_infers_language_when_tag_missing(self, assistant, mock_ai_core):
        mock_ai_core._ollama_chat.return_value = "```\ndef foo():\n    return 1\n```"
        result = await assistant.handle("write a python function")
        assert result["language"] == "python"

    @pytest.mark.asyncio
    async def test_handle_graceful_on_ollama_error(self, assistant, mock_ai_core):
        mock_ai_core._ollama_chat.side_effect = Exception("connection refused")
        result = await assistant.handle("write something")
        assert result["message_type"] == "text"
        assert "try again" in result["text"].lower()
