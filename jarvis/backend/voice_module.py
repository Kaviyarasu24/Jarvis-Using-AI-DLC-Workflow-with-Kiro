"""
VoiceModule — handles speech-to-text (speech_recognition) and
text-to-speech (pyttsx3) with full async/thread safety.
"""

import asyncio
import logging
import threading
from dataclasses import dataclass, field
from typing import Optional

import speech_recognition as sr

from .config_manager import ConfigManager
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Try importing pyttsx3 — gracefully disable TTS if unavailable
# ---------------------------------------------------------------------------
try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not available — TTS disabled.")


@dataclass
class VoiceState:
    enabled: bool = False
    listening: bool = False
    speaking: bool = False
    available: bool = False
    tts_available: bool = False


class VoiceModule:
    """
    Manages voice I/O pipeline:
    - STT: speech_recognition (Google Web Speech API)
    - TTS: pyttsx3 (offline, Windows SAPI5)
    - Emits voice_status WebSocket events on state transitions
    """

    def __init__(
        self,
        config: ConfigManager,
        ws_manager: WebSocketManager,
        recognizer: Optional[sr.Recognizer] = None,
        tts_engine=None,
    ) -> None:
        self._config = config
        self._ws = ws_manager
        self._recognizer = recognizer or sr.Recognizer()
        self._state = VoiceState()
        self._listen_task: Optional[asyncio.Task] = None
        self._tts_lock = threading.Lock()

        # Check microphone availability
        self._state.available = self._check_microphone()

        # Initialize TTS engine
        if tts_engine is not None:
            self._engine = tts_engine
            self._state.tts_available = True
        elif _PYTTSX3_AVAILABLE:
            self._engine = self._init_tts()
        else:
            self._engine = None
            self._state.tts_available = False

        logger.info(
            f"VoiceModule initialized — mic={self._state.available}, "
            f"tts={self._state.tts_available}"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return current voice state as a dict."""
        return {
            "enabled": self._state.enabled,
            "listening": self._state.listening,
            "speaking": self._state.speaking,
            "available": self._state.available,
            "tts_available": self._state.tts_available,
        }

    def is_available(self) -> bool:
        return self._state.available

    async def set_voice_mode(self, enabled: bool) -> None:
        """Enable or disable voice mode."""
        if enabled:
            if not self._state.available:
                await self._ws.send("voice_status", {
                    "status": "error",
                    "error": "Microphone not available",
                })
                return
            self._state.enabled = True
            await self._ws.send("voice_status", {"status": "toggled", "enabled": True})
            # Start the listening loop as a background task
            if self._listen_task is None or self._listen_task.done():
                self._listen_task = asyncio.create_task(self._listen_loop())
        else:
            self._state.enabled = False
            self._state.listening = False
            if self._listen_task and not self._listen_task.done():
                self._listen_task.cancel()
            await self._ws.send("voice_status", {"status": "toggled", "enabled": False})

    async def speak(self, text: str) -> None:
        """Speak text aloud via TTS (non-blocking)."""
        if not self._state.enabled or not self._state.tts_available:
            return
        self._state.speaking = True
        await self._ws.send("voice_status", {"status": "speaking_start"})
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._speak_sync, text)
        finally:
            self._state.speaking = False
            await self._ws.send("voice_status", {"status": "speaking_end"})

    # ------------------------------------------------------------------
    # Internal: listening loop
    # ------------------------------------------------------------------

    async def _listen_loop(self) -> None:
        """Continuously listen for speech while voice mode is enabled."""
        logger.info("Voice listening loop started.")
        while self._state.enabled:
            # Don't listen while TTS is speaking
            if self._state.speaking:
                await asyncio.sleep(0.1)
                continue

            transcribed = await self._listen_once()
            if transcribed:
                # Forward transcribed text to the chat pipeline
                await self._ws.send("user_message_from_voice", {"text": transcribed})

        logger.info("Voice listening loop stopped.")

    async def _listen_once(self) -> Optional[str]:
        """Capture one phrase and return transcribed text, or None on failure."""
        await self._ws.send("voice_status", {"status": "listening_start"})
        self._state.listening = True

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._capture_and_transcribe)
            return result
        finally:
            self._state.listening = False
            await self._ws.send("voice_status", {"status": "listening_end"})

    def _capture_and_transcribe(self) -> Optional[str]:
        """Blocking: capture audio and transcribe. Returns text or None."""
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self._recognizer.listen(
                    source,
                    timeout=self._config.voice_timeout_seconds,
                    phrase_time_limit=self._config.voice_phrase_limit_seconds,
                )
            text = self._recognizer.recognize_google(audio)
            logger.info(f"Transcribed: {text!r}")
            return text.strip() if text.strip() else None

        except sr.WaitTimeoutError:
            # Normal — no speech detected in timeout window
            return None

        except sr.UnknownValueError:
            logger.debug("Speech not understood.")
            # Schedule a friendly message (can't await here — blocking thread)
            asyncio.run_coroutine_threadsafe(
                self._ws.send("chat_response", {
                    "text": "I didn't catch that. Please try again.",
                    "message_type": "text",
                }),
                asyncio.get_event_loop(),
            )
            return None

        except sr.RequestError as e:
            logger.error(f"STT API error: {e}")
            asyncio.run_coroutine_threadsafe(
                self._handle_stt_error(str(e)),
                asyncio.get_event_loop(),
            )
            return None

    async def _handle_stt_error(self, error: str) -> None:
        """Disable voice mode on unrecoverable STT error."""
        self._state.enabled = False
        await self._ws.send("voice_status", {"status": "error", "error": error})
        await self._ws.send("chat_response", {
            "text": "Speech recognition service unavailable. Switching to text mode.",
            "message_type": "text",
        })

    # ------------------------------------------------------------------
    # Internal: TTS
    # ------------------------------------------------------------------

    def _speak_sync(self, text: str) -> None:
        """Blocking TTS — runs in thread executor."""
        with self._tts_lock:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                logger.warning(f"TTS error: {e}")

    # ------------------------------------------------------------------
    # Internal: initialization helpers
    # ------------------------------------------------------------------

    def _check_microphone(self) -> bool:
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.1)
            return True
        except (OSError, AttributeError, Exception) as e:
            logger.warning(f"Microphone not available: {e}")
            return False

    def _init_tts(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self._config.tts_rate)
            self._state.tts_available = True
            return engine
        except Exception as e:
            logger.warning(f"TTS init failed: {e} — TTS disabled.")
            self._state.tts_available = False
            return None
