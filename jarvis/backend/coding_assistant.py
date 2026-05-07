"""
CodingAssistant — IDE-like coding assistance powered by Ollama.
Handles code generation, explanation, debugging, refactoring, and review.

Design notes
------------
- Uses ai_core._ollama_chat() directly so coding context never pollutes the
  main conversation history (same pattern as BrowserModule._summarize).
- Streams tokens back via the WebSocket manager for real-time display.
- Detects task type from keywords; falls back to "generate".
- Extracts code blocks and infers language when Ollama omits the tag.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional, AsyncIterator

from .ai_core import AICore
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Task-specific system prompts
# ---------------------------------------------------------------------------
CODING_PROMPTS: dict[str, str] = {
    "generate": (
        "You are an expert coding assistant. Generate clean, well-commented code. "
        "Always specify the programming language and wrap all code in markdown code blocks "
        "using triple backticks with the language name (e.g. ```python). "
        "After the code, provide a brief explanation of what it does."
    ),
    "explain": (
        "You are an expert coding assistant. Explain the provided code clearly and concisely. "
        "Break down what each part does, explain the logic, and highlight any important patterns or concepts."
    ),
    "debug": (
        "You are an expert debugging assistant. Identify the bug in the provided code, "
        "explain clearly why it occurs, and provide a corrected version wrapped in a markdown code block. "
        "Be specific about what was wrong and how the fix addresses it."
    ),
    "refactor": (
        "You are an expert coding assistant specializing in code quality. "
        "Refactor the provided code to be cleaner, more efficient, and follow best practices. "
        "Wrap the refactored code in a markdown code block and explain the key improvements made."
    ),
    "review": (
        "You are an expert code reviewer. Review the provided code for: "
        "bugs, security vulnerabilities, performance issues, and style/readability problems. "
        "Provide specific, actionable feedback with examples where relevant."
    ),
}

# Task type detection keywords
_TASK_KEYWORDS: dict[str, list[str]] = {
    "generate": ["generate", "write", "create", "build", "make", "implement",
                 "code for", "function for", "class for"],
    "explain":  ["explain", "what does", "what is this", "how does", "describe",
                 "walk me through"],
    "debug":    ["debug", "fix", "error", "bug", "issue", "broken", "not working",
                 "failing", "exception", "traceback"],
    "refactor": ["refactor", "improve", "clean up", "optimize", "rewrite",
                 "simplify", "restructure"],
    "review":   ["review", "check", "audit", "analyze", "critique",
                 "look at this code", "feedback on"],
}

# Common language keywords for fallback detection when Ollama omits the tag
_LANG_HINTS: list[tuple[str, list[str]]] = [
    ("java",       ["public class", "System.out", "void main", "import java"]),
    ("csharp",     ["using System", "Console.Write", "namespace ", "public class"]),
    ("cpp",        ["#include", "std::", "cout <<", "int main("]),
    ("typescript", ["interface ", ": string", ": number", ": boolean", "type "]),
    ("javascript", ["const ", "let ", "var ", "function ", "=>", "console.log"]),
    ("python",     ["def ", "import ", "print(", "elif ", "lambda ", "    pass"]),
    ("go",         ["func ", "package main", "fmt.Print", ":= "]),
    ("rust",       ["fn main", "let mut", "println!", "use std"]),
    ("sql",        ["SELECT ", "FROM ", "WHERE ", "INSERT INTO", "CREATE TABLE"]),
    ("bash",       ["#!/bin/bash", "echo ", "grep ", "awk ", "sed "]),
    ("html",       ["<!DOCTYPE", "<html", "<div", "<body"]),
    ("css",        ["margin:", "padding:", "color:", "font-size:", "border:"]),
]


@dataclass
class CodeBlock:
    language: str
    content: str


@dataclass
class CodingResponse:
    task_type: str
    language: str
    code: Optional[str]
    explanation: str
    raw: str


class CodingAssistant:
    """Provides IDE-like coding assistance using Ollama with task-specific prompts."""

    def __init__(self, ai_core: AICore, ws_manager: Optional[WebSocketManager] = None) -> None:
        self._ai_core = ai_core
        self._ws = ws_manager  # optional — used for streaming

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        """
        Detect task type, stream response via WebSocket if ws_manager is set,
        otherwise return full response dict.

        Uses _ollama_chat directly to avoid polluting conversation history
        with large code blocks.
        """
        task_type = self.detect_task_type(message)
        system_prompt = CODING_PROMPTS[task_type]
        logger.info(f"Coding task: {task_type!r} | {message[:60]!r}")

        if self._ws:
            return await self._handle_streaming(message, system_prompt, task_type)
        return await self._handle_blocking(message, system_prompt)

    def detect_task_type(self, message: str) -> str:
        """Detect coding task type from message keywords."""
        msg_lower = message.lower()
        for task_type, keywords in _TASK_KEYWORDS.items():
            if any(kw in msg_lower for kw in keywords):
                return task_type
        return "generate"

    # ------------------------------------------------------------------
    # Internal: streaming path
    # ------------------------------------------------------------------

    async def _handle_streaming(self, message: str, system_prompt: str, task_type: str) -> dict:
        """Stream tokens to the frontend via WebSocket."""
        import uuid
        msg_id = uuid.uuid4().hex
        full_text = ""

        await self._ws.send("stream_start", {"id": msg_id})

        try:
            async for token, done in self._stream_ollama(message, system_prompt):
                full_text += token
                await self._ws.send("stream_token", {"id": msg_id, "token": token, "done": done})
        except Exception as e:
            logger.error(f"Coding stream error: {e}")
            await self._ws.send("stream_token", {
                "id": msg_id,
                "token": f"\n\n[Error: {e}]",
                "done": True,
            })

        return {"__streamed__": True}

    async def _stream_ollama(self, message: str, system_prompt: str):
        """Async generator — yields (token, done) from Ollama streaming API."""
        import httpx, json as _json
        payload = {
            "model": self._ai_core._config.ollama_model,
            "messages": [{"role": "user", "content": message}],
            "stream": True,
            "system": system_prompt,
        }
        url = f"{self._ai_core._config.ollama_base_url}/api/chat"

        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = _json.loads(line)
                    except _json.JSONDecodeError:
                        continue
                    token = chunk.get("message", {}).get("content", "")
                    done = chunk.get("done", False)
                    yield token, done
                    if done:
                        break

    # ------------------------------------------------------------------
    # Internal: blocking path (no ws_manager — used in tests / fallback)
    # ------------------------------------------------------------------

    async def _handle_blocking(self, message: str, system_prompt: str) -> dict:
        """Non-streaming fallback — calls Ollama directly, bypasses history."""
        try:
            raw_response = await self._ai_core._ollama_chat(
                messages=[{"role": "user", "content": message}],
                system=system_prompt,
            )
        except Exception as e:
            logger.error(f"Coding assistant error: {e}")
            return {"text": "Sorry, I couldn't process that coding request. Please try again.",
                    "message_type": "text"}

        code_blocks = self._extract_code_blocks(raw_response)
        if code_blocks:
            lang = code_blocks[0].language
            if lang == "text":
                lang = self._infer_language(code_blocks[0].content)
            return {"text": raw_response, "message_type": "code", "language": lang}
        return {"text": raw_response, "message_type": "text"}

    # ------------------------------------------------------------------
    # Internal: parsing helpers
    # ------------------------------------------------------------------

    def _extract_code_blocks(self, text: str) -> list[CodeBlock]:
        """Extract all markdown code blocks from text."""
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [
            CodeBlock(
                language=lang.strip() or "text",
                content=code.strip(),
            )
            for lang, code in matches
        ]

    def _infer_language(self, code: str) -> str:
        """Guess language from code content when Ollama omits the tag."""
        for lang, hints in _LANG_HINTS:
            if any(hint in code for hint in hints):
                return lang
        return "text"
