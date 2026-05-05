"""Unit tests for CodingAssistant."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.coding_assistant import CodingAssistant, CodeBlock


@pytest.fixture
def mock_ai_core():
    core = AsyncMock()
    core.chat = AsyncMock(return_value="```python\nprint('hello')\n```\nThis prints hello.")
    return core


@pytest.fixture
def assistant(mock_ai_core):
    return CodingAssistant(ai_core=mock_ai_core)


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


class TestHandle:
    @pytest.mark.asyncio
    async def test_handle_returns_code_message_type(self, assistant):
        result = await assistant.handle("write a hello world in python")
        assert result["message_type"] == "code"
        assert result["language"] == "python"

    @pytest.mark.asyncio
    async def test_handle_returns_text_when_no_code_block(self, assistant, mock_ai_core):
        mock_ai_core.chat.return_value = "This is just an explanation with no code."
        result = await assistant.handle("explain recursion")
        assert result["message_type"] == "text"

    @pytest.mark.asyncio
    async def test_handle_uses_correct_system_prompt(self, assistant, mock_ai_core):
        await assistant.handle("debug this error")
        call_kwargs = mock_ai_core.chat.call_args
        system_prompt = call_kwargs[1].get("system_prompt") or call_kwargs[0][1]
        assert "debug" in system_prompt.lower() or "bug" in system_prompt.lower()
