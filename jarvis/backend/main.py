"""
JARVIS — FastAPI backend entry point.
Handles startup/shutdown lifecycle, CORS, WebSocket route, and REST endpoints.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config_manager import ConfigManager
from .data_init import initialize_data_directory
from .websocket_manager import WebSocketManager
from .voice_module import VoiceModule
from .ai_core import AICore, JARVIS_SYSTEM_PROMPT
from .intent_router import IntentRouter
from .system_controller import SystemController
from .system_monitor import SystemMonitor
from .browser_module import BrowserModule
from .coding_assistant import CodingAssistant
from .calendar_manager import CalendarManager
from .news_module import fetch_news

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application state (module-level singletons)
# ---------------------------------------------------------------------------
config = ConfigManager()
ws_manager = WebSocketManager()
voice_module = VoiceModule(config, ws_manager)
ai_core = AICore(config)
intent_router = IntentRouter(ai_core, ws_manager)
system_controller = SystemController(config)
system_monitor = SystemMonitor(config, ws_manager)
browser_module = BrowserModule(config, ai_core)
coding_assistant = CodingAssistant(ai_core)
calendar_manager = CalendarManager(config)


def _setup_handlers() -> None:
    """Register intent handlers on the router."""

    async def chat_handler(message: str) -> dict:
        # Use streaming — send tokens incrementally over WebSocket
        full_text = ""
        msg_id = __import__('uuid').uuid4().hex

        # Send stream_start so frontend creates the message bubble
        await ws_manager.send("stream_start", {"id": msg_id})

        async for token, done in ai_core.chat_stream(message, JARVIS_SYSTEM_PROMPT):
            if _cancel_requested:
                await ws_manager.send("stream_end", {"id": msg_id, "cancelled": True})
                return {"__streamed__": True}
            full_text += token
            await ws_manager.send("stream_token", {"id": msg_id, "token": token, "done": done})

        # Speak response if voice mode is active
        if voice_module._state.enabled and full_text:
            import asyncio as _asyncio
            _asyncio.create_task(voice_module.speak(full_text))

        return {"__streamed__": True}  # signal that response was already sent

    async def voice_control_handler(message: str) -> dict:
        msg_lower = message.lower()
        enable = any(w in msg_lower for w in ("on", "enable", "start", "activate"))
        await voice_module.set_voice_mode(enable)
        state = "enabled" if enable else "disabled"
        return {"text": f"Voice mode {state}.", "message_type": "text"}

    intent_router.register_handler("chat", chat_handler)
    intent_router.register_handler("voice_control", voice_control_handler)

    async def system_handler(message: str) -> dict:
        result = await system_controller.handle(message)
        return result

    intent_router.register_handler("system", system_handler)

    async def browser_handler(message: str) -> dict:
        return await browser_module.handle(message)

    intent_router.register_handler("search", browser_handler)

    async def coding_handler(message: str) -> dict:
        return await coding_assistant.handle(message)

    intent_router.register_handler("code", coding_handler)

    async def calendar_handler(message: str) -> dict:
        return await calendar_manager.handle(message)

    intent_router.register_handler("calendar", calendar_handler)


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("JARVIS starting up...")
    initialize_data_directory(config.data_dir)
    logger.info(f"Ollama model: {config.ollama_model} @ {config.ollama_base_url}")
    logger.info(f"Voice available: {voice_module.is_available()}")
    _setup_handlers()
    await system_monitor.start()
    # Verify Ollama connectivity on startup
    ollama_ok = await ai_core.health_check()
    if ollama_ok:
        logger.info(f"✓ Ollama reachable at {config.ollama_base_url} — model: {config.ollama_model}")
    else:
        logger.warning(f"✗ Ollama NOT reachable at {config.ollama_base_url} — chat will fail until Ollama is running")
    logger.info("JARVIS ready.")
    yield
    # Shutdown
    await system_monitor.stop()
    logger.info("JARVIS shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="JARVIS",
    description="AI-powered personal assistant backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server and local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # fallback
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    """Health check endpoint — returns backend status."""
    return {
        "status": "ok",
        "ollama_model": config.ollama_model,
        "websocket_connected": ws_manager.is_connected,
        "voice_available": voice_module.is_available(),
    }


# ---------------------------------------------------------------------------
# Calendar REST Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/tasks")
async def get_all_tasks():
    return {"tasks": calendar_manager.tasks_as_dicts()}


@app.get("/api/tasks/today")
async def get_today_tasks():
    from dataclasses import asdict
    return {"tasks": [asdict(t) for t in calendar_manager.get_today_tasks()]}


@app.get("/api/tasks/tomorrow")
async def get_tomorrow_tasks():
    from dataclasses import asdict
    return {"tasks": [asdict(t) for t in calendar_manager.get_tomorrow_tasks()]}


@app.get("/api/tasks/date/{task_date}")
async def get_tasks_by_date(task_date: str):
    from dataclasses import asdict
    return {"tasks": [asdict(t) for t in calendar_manager.get_tasks_for_date(task_date)]}


@app.post("/api/tasks", status_code=201)
async def create_task(body: dict):
    title = body.get("title", "").strip()
    if not title:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="title is required")
    task_date = body.get("date") or _today_str()
    description = body.get("description", "")
    from dataclasses import asdict
    task = calendar_manager.add_task(title, task_date, description)
    return asdict(task)


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    removed = calendar_manager.remove_task(task_id=task_id)
    if not removed:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}


@app.get("/api/reminders")
async def get_reminders():
    from dataclasses import asdict
    return {"tasks": [asdict(t) for t in calendar_manager.get_reminders()]}


# ---------------------------------------------------------------------------
# News Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/news")
async def get_news(topic: str = "top", limit: int = 20):
    """Fetch news headlines from Google News RSS. No API key required."""
    import asyncio
    loop = asyncio.get_event_loop()
    items = await loop.run_in_executor(None, lambda: fetch_news(topic, limit))
    return {"topic": topic, "items": items}


@app.get("/api/news/topics")
async def get_news_topics():
    """Return available news topic categories."""
    return {"topics": ["top", "technology", "science", "business", "health", "sports", "world"]}


def _today_str() -> str:
    from datetime import date
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Cancel endpoint — aborts current processing
# ---------------------------------------------------------------------------
_cancel_requested = False


@app.post("/api/cancel")
async def cancel_generation():
    """Signal the backend to cancel the current in-progress generation."""
    global _cancel_requested
    _cancel_requested = True
    return {"status": "cancelled"}


@app.post("/api/test-alert")
async def test_alert():
    """Fire a test alert to verify the notification pipeline."""
    import uuid
    from datetime import datetime, timezone
    await ws_manager.broadcast("alert", {
        "id": str(uuid.uuid4()),
        "type": "wifi_connected",
        "message": "🔔 Test alert — notifications are working!",
        "severity": "info",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "sent"}

# ---------------------------------------------------------------------------
# WebSocket Endpoint
# ---------------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            msg = await ws_manager.receive(websocket)
            await _handle_message(msg)
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket)


async def _handle_message(msg: dict) -> None:
    """Route incoming WebSocket messages to the appropriate handler."""
    msg_type = msg.get("type", "__unknown__")
    payload = msg.get("payload", {})

    try:
        if msg_type == "user_message":
            text = payload.get("text", "")
            if text.strip():
                global _cancel_requested
                _cancel_requested = False  # reset on new message
                response = await intent_router.route(text)
                if _cancel_requested:
                    # Frontend already showed "Generation stopped." — don't send again
                    _cancel_requested = False
                    return
                if isinstance(response, dict) and response.get("type") == "confirmation_required":
                    await ws_manager.send(response["type"], response["payload"])
                elif isinstance(response, dict) and response.get("__streamed__"):
                    pass  # streaming handler already sent all tokens
                else:
                    await ws_manager.send("chat_response", response)

        elif msg_type == "voice_toggle":
            enabled = payload.get("enabled", False)
            await voice_module.set_voice_mode(enabled)

        elif msg_type == "user_message_from_voice":
            text = payload.get("text", "")
            if text.strip():
                response = await intent_router.route(text)
                if isinstance(response, dict) and response.get("type") == "confirmation_required":
                    await ws_manager.send(response["type"], response["payload"])
                elif isinstance(response, dict) and response.get("__streamed__"):
                    pass
                else:
                    await ws_manager.send("chat_response", response)

        elif msg_type == "confirm_action":
            action_id = payload.get("action_id", "")
            result = await system_controller.confirm_action(action_id)
            await ws_manager.send("chat_response", result)

        elif msg_type == "clear_history":
            ai_core.clear_history()
            await ws_manager.send("chat_response", {
                "text": "Conversation history cleared.",
                "message_type": "text",
            })

        elif msg_type == "__invalid__":
            await ws_manager.send("error", {
                "message": "Invalid message format",
                "code": "INVALID_FORMAT",
            })

        else:
            logger.warning(f"Unhandled message type: {msg_type}")
            await ws_manager.send("error", {
                "message": f"Unknown message type: {msg_type}",
                "code": "UNKNOWN_TYPE",
            })

    except Exception as e:
        logger.error(f"Error handling message type '{msg_type}': {e}", exc_info=True)
        try:
            await ws_manager.send("chat_response", {
                "text": "Sorry, something went wrong. Please try again.",
                "message_type": "text",
            })
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Serve React frontend static files (production build)
# ---------------------------------------------------------------------------
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
    logger.info(f"Serving React frontend from {_frontend_dist}")


# ---------------------------------------------------------------------------
# Entry point (run directly with: python -m backend.main)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=config.backend_port,
        reload=True,
    )
