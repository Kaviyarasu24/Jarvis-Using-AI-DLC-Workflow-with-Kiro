"""
AICore — Ollama LLM integration with persistent conversation history.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------
JARVIS_SYSTEM_PROMPT = (
    "You are JARVIS, an intelligent AI-powered personal assistant. "
    "You help with general questions, coding, web searches, system tasks, and scheduling. "
    "Be concise, helpful, and friendly. When you don't know something, say so clearly."
)

CODING_SYSTEM_PROMPT = (
    "You are JARVIS, an expert coding assistant. "
    "Help with code generation, explanation, debugging, refactoring, and code review. "
    "Always provide clean, well-commented code. Specify the programming language in your response. "
    "Format code blocks using markdown triple backticks with the language name."
)

INTENT_CLASSIFICATION_PROMPT = """\
Classify the following user message into exactly one category.
Respond with ONLY the category name, nothing else.

Categories: chat, code, search, system, calendar, voice_control

Rules:
- chat: general conversation, questions, explanations, anything not in other categories
- code: writing, debugging, explaining, reviewing, or refactoring code/programs
- search: requests to search the web, find online information, look something up
- system: file operations, launching apps, running commands, OS control, open URLs
- calendar: tasks, reminders, scheduling, to-do items, events
- voice_control: turn on/off voice, enable/disable microphone, voice mode

Message: {message}"""

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------
class OllamaUnavailableError(Exception):
    pass

class OllamaTimeoutError(Exception):
    pass


# ---------------------------------------------------------------------------
# AICore
# ---------------------------------------------------------------------------
class AICore:
    """Manages Ollama LLM interactions and conversation history."""

    def __init__(self, config: ConfigManager, http_client: Optional[httpx.AsyncClient] = None) -> None:
        self._config = config
        self._http_client = http_client  # injected for testing
        self._messages: list[dict] = []
        self._history_path = Path(config.data_dir) / "conversation_history.json"
        self.load_history()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(self, message: str, system_prompt: str = JARVIS_SYSTEM_PROMPT) -> str:
        """Send a message to Ollama and return the full response text (non-streaming).
        Used by non-chat handlers (coding, calendar, etc.) that need the complete response."""
        self._append_message("user", message)
        context = self.get_context_window(self._config.history_context_window)

        try:
            response_text = await self._ollama_chat(context, system_prompt)
        except asyncio.CancelledError:
            response_text = "Generation stopped."
        except OllamaUnavailableError:
            response_text = (
                "I'm having trouble connecting to my AI engine. "
                "Please make sure Ollama is running (`ollama serve`)."
            )
        except OllamaTimeoutError:
            response_text = "The response took too long. Please try again."
        except Exception as e:
            logger.error(f"Unexpected Ollama error: {e}")
            response_text = "Something went wrong. Please try again."

        self._append_message("assistant", response_text)
        self.save_history()
        return response_text

    async def chat_stream(
        self,
        message: str,
        system_prompt: str = JARVIS_SYSTEM_PROMPT,
    ):
        """Stream tokens from Ollama as an async generator.
        Yields (token: str, done: bool) tuples.
        Caller is responsible for appending the full response to history."""
        self._append_message("user", message)
        context = self.get_context_window(self._config.history_context_window)

        payload: dict = {
            "model": self._config.ollama_model,
            "messages": context,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        url = f"{self._config.ollama_base_url}/api/chat"
        full_response = ""

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        token = chunk.get("message", {}).get("content", "")
                        done = chunk.get("done", False)
                        full_response += token
                        yield token, done

                        if done:
                            break

        except httpx.ConnectError as e:
            yield "I'm having trouble connecting to my AI engine. Please make sure Ollama is running.", True
        except httpx.TimeoutException:
            yield "The response took too long. Please try again.", True
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield "Something went wrong. Please try again.", True
        finally:
            if full_response:
                self._append_message("assistant", full_response)
                self.save_history()

    async def classify_intent(self, message: str) -> str:
        """Legacy method — IntentRouter now handles full extraction directly.
        Kept for backward compatibility with tests."""
        msg_lower = message.lower().strip()
        _KEYWORD_MAP = [
            (["write ", "generate ", "debug ", "fix this", "explain this code",
              "refactor ", "review this code"], "code"),
            (["search for", "look up", "google ", "find online"], "search"),
            (["open ", "launch ", "list files", "delete file", "run command"], "system"),
            (["add task", "remind me", "show tasks", "list tasks"], "calendar"),
            (["enable voice", "disable voice", "turn on voice", "turn off voice"], "voice_control"),
        ]
        for keywords, intent in _KEYWORD_MAP:
            if any(kw in msg_lower for kw in keywords):
                return intent
        return "chat"

    def load_history(self) -> None:
        """Load conversation history from JSON file."""
        try:
            if self._history_path.exists():
                with open(self._history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._messages = data.get("messages", [])
                logger.info(f"Loaded {len(self._messages)} messages from history.")
            else:
                self._messages = []
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load history: {e}. Starting fresh.")
            self._messages = []

    def save_history(self) -> None:
        """Persist conversation history to JSON (atomic write)."""
        try:
            tmp = self._history_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"messages": self._messages}, f, indent=2, ensure_ascii=False)
            tmp.replace(self._history_path)
        except OSError as e:
            logger.error(f"Failed to save history: {e}")

    def clear_history(self) -> None:
        """Clear in-memory and persisted conversation history."""
        self._messages = []
        self.save_history()
        logger.info("Conversation history cleared.")

    def get_context_window(self, n: int) -> list[dict]:
        """Return last N messages formatted for Ollama."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self._messages[-n:]
        ]

    def append_to_history(self, role: str, content: str) -> None:
        """Append a message to history (used by other modules)."""
        self._append_message(role, content)

    async def health_check(self) -> bool:
        """Return True if Ollama API is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._config.ollama_base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _append_message(self, role: str, content: str) -> None:
        self._messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    async def _ollama_chat(self, messages: list[dict], system: Optional[str]) -> str:
        """Make a POST request to Ollama /api/chat and return response text."""
        payload: dict = {
            "model": self._config.ollama_model,
            "messages": messages,
            "stream": False,
        }
        if system:
            payload["system"] = system

        url = f"{self._config.ollama_base_url}/api/chat"

        try:
            if self._http_client:
                # Injected client (used in tests)
                response = await self._http_client.post(url, json=payload)
            else:
                async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                    response = await client.post(url, json=payload)

            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]

        except httpx.ConnectError as e:
            raise OllamaUnavailableError(str(e)) from e
        except httpx.ConnectTimeout as e:
            raise OllamaUnavailableError(str(e)) from e
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(str(e)) from e
        except (KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Unexpected Ollama response format: {e}") from e
