"""
SystemController — executes OS-level operations with a confirmation gate
for destructive actions.
"""

import asyncio
import logging
import os
import re
import shutil
import subprocess
import uuid
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

COMMAND_TIMEOUT = 30  # seconds
CONFIRMATION_TTL = 60  # seconds


@dataclass
class ActionResult:
    success: bool
    output: Optional[str] = None
    requires_confirmation: bool = False
    action_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PendingAction:
    action_id: str
    action_type: str
    params: dict
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SystemController:
    """Handles OS-level operations with a two-phase confirmation gate for destructive ops."""

    def __init__(self, config: ConfigManager) -> None:
        self._config = config
        self._pending: dict[str, PendingAction] = {}

    # ------------------------------------------------------------------
    # Public: parse and dispatch natural language system command
    # ------------------------------------------------------------------

    async def handle(self, message: str) -> dict:
        """Parse a natural language system command and execute it."""
        result = await self._dispatch(message)
        if result.requires_confirmation:
            return {
                "type": "confirmation_required",
                "payload": {
                    "action_id": result.action_id,
                    "action": self._pending[result.action_id].action_type,
                    "details": self._pending[result.action_id].params.get("details", ""),
                },
            }
        if result.success:
            return {"text": result.output or "Done.", "message_type": "text"}
        return {"text": f"Error: {result.error}", "message_type": "text"}

    async def confirm_action(self, action_id: str) -> dict:
        """Execute a previously pending destructive action after user confirmation."""
        action = self._pending.pop(action_id, None)
        if action is None:
            return {"text": "Action expired or not found.", "message_type": "text"}

        if action.action_type == "delete_file":
            result = await self.delete_file(action.params["path"], confirmed=True)
        elif action.action_type == "run_command":
            result = await self.run_command(action.params["command"], confirmed=True)
        else:
            return {"text": "Unknown action type.", "message_type": "text"}

        if result.success:
            return {"text": result.output or "Done.", "message_type": "text"}
        return {"text": f"Error: {result.error}", "message_type": "text"}

    # ------------------------------------------------------------------
    # Individual operations
    # ------------------------------------------------------------------

    async def open_url(self, url: str) -> ActionResult:
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, webbrowser.open, url)
            return ActionResult(success=True, output=f"Opened URL: {url}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def launch_app(self, app_name: str) -> ActionResult:
        try:
            loop = asyncio.get_event_loop()
            if os.name == "nt":  # Windows
                await loop.run_in_executor(None, lambda: os.startfile(app_name))
            else:
                await loop.run_in_executor(None, lambda: subprocess.Popen([app_name]))
            return ActionResult(success=True, output=f"Launched: {app_name}")
        except Exception as e:
            return ActionResult(success=False, error=f"Could not launch '{app_name}': {e}")

    async def list_directory(self, path: str) -> ActionResult:
        try:
            p = Path(path).expanduser()
            if not p.exists():
                return ActionResult(success=False, error=f"Path not found: {path}")
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
            lines = [f"{'[DIR] ' if e.is_dir() else '      '}{e.name}" for e in entries]
            return ActionResult(success=True, output="\n".join(lines) or "(empty directory)")
        except PermissionError:
            return ActionResult(success=False, error=f"Permission denied: {path}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def read_file(self, path: str) -> ActionResult:
        try:
            p = Path(path).expanduser()
            if not p.exists():
                return ActionResult(success=False, error=f"File not found: {path}")
            if p.stat().st_size > 100_000:  # 100KB limit
                return ActionResult(success=False, error="File too large to display (>100KB).")
            content = p.read_text(encoding="utf-8", errors="replace")
            return ActionResult(success=True, output=content)
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def copy_file(self, src: str, dst: str) -> ActionResult:
        try:
            loop = asyncio.get_event_loop()
            s, d = Path(src).expanduser(), Path(dst).expanduser()
            if not s.exists():
                return ActionResult(success=False, error=f"Source not found: {src}")
            await loop.run_in_executor(None, shutil.copy2, str(s), str(d))
            return ActionResult(success=True, output=f"Copied {src} → {dst}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def move_file(self, src: str, dst: str) -> ActionResult:
        try:
            loop = asyncio.get_event_loop()
            s = Path(src).expanduser()
            if not s.exists():
                return ActionResult(success=False, error=f"Source not found: {src}")
            await loop.run_in_executor(None, shutil.move, str(s), dst)
            return ActionResult(success=True, output=f"Moved {src} → {dst}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def delete_file(self, path: str, confirmed: bool = False) -> ActionResult:
        if not confirmed:
            action_id = str(uuid.uuid4())
            self._pending[action_id] = PendingAction(
                action_id=action_id,
                action_type="delete_file",
                params={"path": path, "details": f"Delete: {path}"},
            )
            return ActionResult(requires_confirmation=True, action_id=action_id)
        try:
            p = Path(path).expanduser()
            if not p.exists():
                return ActionResult(success=False, error=f"Not found: {path}")
            loop = asyncio.get_event_loop()
            if p.is_dir():
                await loop.run_in_executor(None, shutil.rmtree, str(p))
            else:
                await loop.run_in_executor(None, p.unlink)
            return ActionResult(success=True, output=f"Deleted: {path}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    async def run_command(self, command: str, confirmed: bool = False) -> ActionResult:
        if not confirmed:
            action_id = str(uuid.uuid4())
            self._pending[action_id] = PendingAction(
                action_id=action_id,
                action_type="run_command",
                params={"command": command, "details": f"Run command: {command}"},
            )
            return ActionResult(requires_confirmation=True, action_id=action_id)
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=COMMAND_TIMEOUT,
                ),
            )
            output = result.stdout or result.stderr or "(no output)"
            return ActionResult(success=result.returncode == 0, output=output.strip())
        except subprocess.TimeoutExpired:
            return ActionResult(success=False, error=f"Command timed out after {COMMAND_TIMEOUT}s")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    # ------------------------------------------------------------------
    # Internal: natural language command parser
    # ------------------------------------------------------------------

    async def _dispatch(self, message: str) -> ActionResult:
        """Parse natural language and dispatch to the right operation."""
        msg = message.strip()
        msg_lower = msg.lower()

        # Open URL
        url_match = re.search(r'https?://\S+', msg)
        if url_match or any(w in msg_lower for w in ("open url", "open http", "browse to")):
            url = url_match.group(0) if url_match else msg.split()[-1]
            return await self.open_url(url)

        # Launch app
        if any(msg_lower.startswith(w) for w in ("open ", "launch ", "start ")):
            app = re.sub(r'^(open|launch|start)\s+', '', msg, flags=re.IGNORECASE).strip()
            if not app.startswith("http"):
                return await self.launch_app(app)

        # List directory
        if any(w in msg_lower for w in ("list files", "list directory", "ls ", "dir ")):
            path_match = re.search(r'(?:in|at|of)?\s+([^\s].+)$', msg, re.IGNORECASE)
            path = path_match.group(1).strip() if path_match else "."
            return await self.list_directory(path)

        # Read file
        if any(w in msg_lower for w in ("read file", "show file", "cat ", "open file")):
            path_match = re.search(r'(?:file|cat)\s+(.+)$', msg, re.IGNORECASE)
            path = path_match.group(1).strip() if path_match else ""
            if path:
                return await self.read_file(path)

        # Delete file
        if any(w in msg_lower for w in ("delete ", "remove file", "rm ")):
            path_match = re.search(r'(?:delete|remove|rm)\s+(.+)$', msg, re.IGNORECASE)
            path = path_match.group(1).strip() if path_match else ""
            if path:
                return await self.delete_file(path)

        # Run command
        if any(msg_lower.startswith(w) for w in ("run ", "execute ", "cmd ", "terminal ")):
            cmd = re.sub(r'^(run|execute|cmd|terminal)\s+', '', msg, flags=re.IGNORECASE).strip()
            return await self.run_command(cmd)

        # Fallback
        return ActionResult(success=False, error="I couldn't understand that system command. Try: 'open <app>', 'list files in <path>', 'run <command>', etc.")
