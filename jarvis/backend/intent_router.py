"""
IntentRouter — uses LLM structured extraction to understand any natural language
input and dispatch to the correct handler with extracted parameters.
"""

import json
import logging
import re
from typing import Callable, Awaitable

from .ai_core import AICore, JARVIS_SYSTEM_PROMPT
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

HandlerFunc = Callable[[str], Awaitable[dict]]

# ---------------------------------------------------------------------------
# Structured extraction prompt
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = """\
You are JARVIS, an AI assistant. Analyze the user's message and return a JSON object describing what action to take.

Return ONLY valid JSON — no explanation, no markdown, no extra text.

JSON format:
{{
  "intent": "<one of: chat, code, search, system, calendar, voice_control>",
  "action": "<specific action or null>",
  "params": {{ <extracted parameters or empty object> }}
}}

Intent and action guide:
- "chat": general conversation → action: "respond"
- "code": coding help → action: one of "generate", "explain", "debug", "refactor", "review"
- "search": web search → action: "search", params: {{"query": "<search query>"}}
- "system": OS operations → action: one of:
    "launch_app" with params: {{"app": "<app name>"}}
    "open_url" with params: {{"url": "<url>"}}
    "list_directory" with params: {{"path": "<path>"}}
    "read_file" with params: {{"path": "<file path>"}}
    "delete_file" with params: {{"path": "<file path>"}}
    "run_command" with params: {{"command": "<shell command>"}}
- "calendar": task management → action: one of:
    "add_task" with params: {{"title": "<task>", "date": "<YYYY-MM-DD or today/tomorrow>"}}
    "remove_task" with params: {{"title": "<task title>"}}
    "view_tasks" with params: {{"filter": "<all|today|tomorrow>"}}
    "reminders" with params: {{}}
- "voice_control": voice toggle → action: "enable" or "disable"

Examples:
User: "can you help me open notepad"
→ {{"intent": "system", "action": "launch_app", "params": {{"app": "notepad"}}}}

User: "please search for python tutorials online"
→ {{"intent": "search", "action": "search", "params": {{"query": "python tutorials"}}}}

User: "remind me to call mom tomorrow"
→ {{"intent": "calendar", "action": "add_task", "params": {{"title": "call mom", "date": "tomorrow"}}}}

User: "write a function to reverse a string"
→ {{"intent": "code", "action": "generate", "params": {{}}}}

User: "hi how are you"
→ {{"intent": "chat", "action": "respond", "params": {{}}}}

User message: {message}"""


class IntentRouter:
    """
    Routes user messages using LLM structured extraction.
    The LLM returns a JSON action object — no rigid keyword matching needed.
    Any natural language phrasing is handled correctly.
    """

    def __init__(self, ai_core: AICore, ws_manager: WebSocketManager) -> None:
        self._ai_core = ai_core
        self._ws = ws_manager
        self._handlers: dict[str, HandlerFunc] = {}

    def register_handler(self, intent: str, handler: HandlerFunc) -> None:
        self._handlers[intent] = handler
        logger.info(f"Registered handler for intent: {intent}")

    async def route(self, message: str) -> dict:
        """Extract structured intent+action from message, dispatch to handler."""
        extraction = await self._extract(message)
        intent = extraction.get("intent", "chat")
        action = extraction.get("action", "respond")
        params = extraction.get("params", {})

        logger.info(f"Extracted: intent={intent!r} action={action!r} params={params} | msg={message[:60]!r}")

        # Build a context-enriched message for the handler
        # Pass original message + extracted params so handlers can use either
        enriched = self._build_enriched_message(message, intent, action, params)

        handler = self._handlers.get(intent) or self._handlers.get("chat")
        if handler:
            try:
                return await handler(enriched)
            except Exception as e:
                logger.error(f"Handler error for intent '{intent}': {e}")
                return {"text": "Something went wrong. Please try again.", "message_type": "text"}

        # Absolute fallback
        text = await self._ai_core.chat(message, JARVIS_SYSTEM_PROMPT)
        return {"text": text, "message_type": "text"}

    async def _extract(self, message: str) -> dict:
        """Call LLM to extract structured intent+action+params from message.
        First tries fast keyword detection, only calls LLM for truly ambiguous cases."""

        # Try keyword fallback first — it's instant and handles most cases
        keyword_result = self._keyword_fallback(message)

        # If keyword detection found a non-chat intent, use it directly (no LLM needed)
        if keyword_result.get("intent") != "chat":
            logger.info(f"Intent resolved by keyword: {keyword_result}")
            return keyword_result

        # For chat messages, try LLM extraction with a short timeout
        prompt = EXTRACTION_PROMPT.format(message=message)
        try:
            raw = await self._ai_core._ollama_chat(
                messages=[{"role": "user", "content": prompt}],
                system=None,
            )
            # Strip markdown code fences if present
            raw = re.sub(r'```(?:json)?\s*', '', raw).strip()

            # Try to find a JSON object anywhere in the response
            json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                logger.info(f"Intent resolved by LLM: {result}")
                return result

            # If response looks like key:value pairs without braces, wrap it
            if '"intent"' in raw:
                wrapped = '{' + raw.strip().strip(',') + '}'
                return json.loads(wrapped)

            return json.loads(raw)

        except Exception as e:
            logger.warning(f"LLM extraction failed ({e!r}) — using keyword fallback")
            return keyword_result

    def _keyword_fallback(self, message: str) -> dict:
        """Fast keyword fallback — covers broad natural language patterns."""
        msg = message.lower().strip()

        # ── System: launch app ──────────────────────────────────────────────
        # Matches: "open X", "launch X", "start X", "can you open X",
        #          "please open X", "help me open X", "I need X open"
        _APPS = r'(notepad|chrome|firefox|edge|calculator|explorer|file explorer|cmd|command prompt|terminal|powershell|word|excel|powerpoint|vlc|spotify|paint|task manager|control panel|settings|camera|photos|calendar|clock|maps|mail|outlook|teams|zoom|discord|vscode|visual studio|code|pycharm|intellij|android studio|obs|steam|epic games|brave|opera)'
        app_match = re.search(
            r'(?:open|launch|start|run|load|bring up|pull up|show me|can you open|please open|help.*open|need.*open|want.*open|could you open|would you open)\s+' + _APPS,
            msg
        )
        if app_match:
            return {"intent": "system", "action": "launch_app", "params": {"app": app_match.group(1)}}

        # Also catch "open notepad for me", "open the notepad"
        app_match2 = re.search(r'\b(?:open|launch|start)\b.*\b' + _APPS + r'\b', msg)
        if app_match2:
            return {"intent": "system", "action": "launch_app", "params": {"app": app_match2.group(1)}}

        # ── System: open URL ────────────────────────────────────────────────
        if re.search(r'https?://', msg):
            url_match = re.search(r'https?://\S+', msg)
            return {"intent": "system", "action": "open_url", "params": {"url": url_match.group(0) if url_match else msg}}

        # ── System: file operations ─────────────────────────────────────────
        if re.search(r'\b(list|show|display)\b.*(files?|folder|directory|dir)\b', msg):
            path_match = re.search(r'(?:in|at|of|from)\s+([A-Za-z]:[^\s]+|\.[\\/][^\s]*|[^\s]+)', msg)
            path = path_match.group(1) if path_match else "."
            return {"intent": "system", "action": "list_directory", "params": {"path": path}}

        if re.search(r'\b(delete|remove|trash)\b.*(file|folder|directory)\b', msg):
            path_match = re.search(r'(?:delete|remove|trash)\s+(?:file|folder)?\s*([^\s]+)', msg)
            return {"intent": "system", "action": "delete_file", "params": {"path": path_match.group(1) if path_match else ""}}

        if re.search(r'\b(run|execute|terminal|cmd)\b.*(command|cmd|script)\b', msg):
            cmd_match = re.search(r'(?:run|execute)\s+(?:command\s+)?(.+)$', msg)
            return {"intent": "system", "action": "run_command", "params": {"command": cmd_match.group(1) if cmd_match else ""}}

        # ── Search ──────────────────────────────────────────────────────────
        if re.search(r'\b(search|find|look up|google|browse|what is|who is|how to|tell me about)\b', msg):
            # Exclude "find file" / "find folder" which are system ops
            if not re.search(r'\b(file|folder|directory)\b', msg):
                query = re.sub(r'^.*(search for|search|look up|google|find|tell me about|what is|who is|how to)\s*', '', msg, flags=re.IGNORECASE).strip()
                return {"intent": "search", "action": "search", "params": {"query": query or message}}

        # ── Code ────────────────────────────────────────────────────────────
        if re.search(r'\b(write|generate|create|make)\b.*(code|function|class|script|program|method)\b', msg):
            return {"intent": "code", "action": "generate", "params": {}}
        if re.search(r'\b(debug|fix|error|bug|exception|traceback|not working|broken)\b', msg):
            return {"intent": "code", "action": "debug", "params": {}}
        if re.search(r'\b(explain|what does|how does|describe)\b.*(code|function|class|script)\b', msg):
            return {"intent": "code", "action": "explain", "params": {}}
        if re.search(r'\b(refactor|improve|optimize|clean up|rewrite)\b.*(code|function|class)\b', msg):
            return {"intent": "code", "action": "refactor", "params": {}}
        if re.search(r'\b(review|check|audit|analyze)\b.*(code|function|class)\b', msg):
            return {"intent": "code", "action": "review", "params": {}}

        # ── Calendar ────────────────────────────────────────────────────────
        if re.search(r'\b(add|create|set|schedule|remind|reminder)\b.*(task|reminder|event|meeting|appointment)\b', msg):
            return {"intent": "calendar", "action": "add_task", "params": {"title": message, "date": "today"}}
        if re.search(r'\bremind me\b', msg):
            return {"intent": "calendar", "action": "add_task", "params": {"title": message, "date": "today"}}
        if re.search(r'\b(show|list|view|what|display)\b.*(task|reminder|schedule|event|appointment)\b', msg):
            filter_val = "today" if "today" in msg else "tomorrow" if "tomorrow" in msg else "all"
            return {"intent": "calendar", "action": "view_tasks", "params": {"filter": filter_val}}
        if re.search(r'\b(remove|delete|cancel)\b.*(task|reminder|event)\b', msg):
            return {"intent": "calendar", "action": "remove_task", "params": {"title": message}}

        # ── Voice control ───────────────────────────────────────────────────
        if re.search(r'\b(enable|turn on|activate|start)\b.*(voice|mic|microphone)\b', msg):
            return {"intent": "voice_control", "action": "enable", "params": {}}
        if re.search(r'\b(disable|turn off|deactivate|stop)\b.*(voice|mic|microphone)\b', msg):
            return {"intent": "voice_control", "action": "disable", "params": {}}

        # ── Default: chat ───────────────────────────────────────────────────
        return {"intent": "chat", "action": "respond", "params": {}}

    def _build_enriched_message(self, original: str, intent: str, action: str, params: dict) -> str:
        """
        Build a message string that handlers can use directly.
        For system/calendar actions, construct a canonical command string
        so existing handlers work without modification.
        """
        if intent == "system":
            if action == "launch_app" and params.get("app"):
                return f"open {params['app']}"
            if action == "open_url" and params.get("url"):
                return f"open {params['url']}"
            if action == "list_directory":
                path = params.get("path", ".")
                return f"list files in {path}"
            if action == "read_file" and params.get("path"):
                return f"read file {params['path']}"
            if action == "delete_file" and params.get("path"):
                return f"delete {params['path']}"
            if action == "run_command" and params.get("command"):
                return f"run {params['command']}"

        if intent == "calendar":
            if action == "add_task":
                title = params.get("title", original)
                date = params.get("date", "today")
                return f"add task {title} for {date}"
            if action == "remove_task" and params.get("title"):
                return f"remove task {params['title']}"
            if action == "view_tasks":
                f = params.get("filter", "all")
                return f"show {f} tasks"
            if action == "reminders":
                return "what are my reminders"

        if intent == "search" and params.get("query"):
            return f"search for {params['query']}"

        if intent == "voice_control":
            return f"{'enable' if action == 'enable' else 'disable'} voice"

        # For chat and code, pass original message unchanged
        return original
