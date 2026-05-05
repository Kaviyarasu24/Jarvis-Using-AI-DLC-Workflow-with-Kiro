"""
CodingAssistant — IDE-like coding assistance powered by Ollama.
Handles code generation, explanation, debugging, refactoring, and review.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from .ai_core import AICore

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
    "generate": ["generate", "write", "create", "build", "make", "implement", "code for", "function for", "class for"],
    "explain":  ["explain", "what does", "what is this", "how does", "describe", "walk me through"],
    "debug":    ["debug", "fix", "error", "bug", "issue", "broken", "not working", "failing", "exception", "traceback"],
    "refactor": ["refactor", "improve", "clean up", "optimize", "rewrite", "simplify", "restructure"],
    "review":   ["review", "check", "audit", "analyze", "critique", "look at this code", "feedback on"],
}


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

    def __init__(self, ai_core: AICore) -> None:
        self._ai_core = ai_core

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        """Detect task type, call Ollama with appropriate prompt, return structured response."""
        task_type = self.detect_task_type(message)
        system_prompt = CODING_PROMPTS[task_type]

        logger.info(f"Coding task type: {task_type!r} for: {message[:60]!r}")

        raw_response = await self._ai_core.chat(message, system_prompt=system_prompt)

        code_blocks = self._extract_code_blocks(raw_response)

        if code_blocks:
            primary = code_blocks[0]
            return {
                "text": raw_response,
                "message_type": "code",
                "language": primary.language or "text",
            }
        return {"text": raw_response, "message_type": "text"}

    def detect_task_type(self, message: str) -> str:
        """Detect coding task type from message keywords."""
        msg_lower = message.lower()
        for task_type, keywords in _TASK_KEYWORDS.items():
            if any(kw in msg_lower for kw in keywords):
                return task_type
        return "generate"  # default

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _extract_code_blocks(self, text: str) -> list[CodeBlock]:
        """Extract all markdown code blocks from text."""
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [
            CodeBlock(language=lang.strip() or "text", content=code.strip())
            for lang, code in matches
        ]
