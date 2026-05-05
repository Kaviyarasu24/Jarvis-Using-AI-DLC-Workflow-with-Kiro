"""Unit tests for VoiceModule."""

from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest
import speech_recognition as sr

from backend.voice_module import VoiceModule, VoiceState
from backend.config_manager import ConfigManager
from backend.websocket_manager import WebSocketManager


@pytest.fixture
def mock_config(tmp_path):
    import json
    cfg = {
        "voice_timeout_seconds": 3,
        "voice_phrase_limit_seconds": 8,
        "tts_rate": 175,
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    return ConfigManager(config_path=str(p))


@pytest.fixture
def mock_ws():
    ws = MagicMock(spec=WebSocketManager)
    ws.send = AsyncMock()
    return ws


@pytest.fixture
def mock_recognizer():
    r = MagicMock(spec=sr.Recognizer)
    r.adjust_for_ambient_noise = MagicMock()
    r.listen = MagicMock()
    r.recognize_google = MagicMock(return_value="hello jarvis")
    return r


@pytest.fixture
def mock_tts_engine():
    engine = MagicMock()
    engine.say = MagicMock()
    engine.runAndWait = MagicMock()
    engine.setProperty = MagicMock()
    return engine


@pytest.fixture
def voice_module(mock_config, mock_ws, mock_recognizer, mock_tts_engine):
    with patch("backend.voice_module.VoiceModule._check_microphone", return_value=True):
        vm = VoiceModule(
            config=mock_config,
            ws_manager=mock_ws,
            recognizer=mock_recognizer,
            tts_engine=mock_tts_engine,
        )
    return vm


class TestVoiceModuleInit:
    def test_mic_unavailable_sets_available_false(self, mock_config, mock_ws):
        with patch("backend.voice_module.VoiceModule._check_microphone", return_value=False):
            vm = VoiceModule(mock_config, mock_ws)
        assert not vm.is_available()

    def test_mic_available_sets_available_true(self, voice_module):
        assert voice_module.is_available()

    def test_get_status_returns_dict(self, voice_module):
        status = voice_module.get_status()
        assert "enabled" in status
        assert "listening" in status
        assert "speaking" in status
        assert "available" in status


class TestVoiceModeToggle:
    @pytest.mark.asyncio
    async def test_enable_voice_mode_when_mic_available(self, voice_module, mock_ws):
        with patch.object(voice_module, "_listen_loop", new_callable=AsyncMock):
            await voice_module.set_voice_mode(True)
        assert voice_module._state.enabled
        mock_ws.send.assert_called_with("voice_status", {"status": "toggled", "enabled": True})

    @pytest.mark.asyncio
    async def test_enable_voice_mode_when_mic_unavailable(self, mock_config, mock_ws, mock_recognizer, mock_tts_engine):
        with patch("backend.voice_module.VoiceModule._check_microphone", return_value=False):
            vm = VoiceModule(mock_config, mock_ws, mock_recognizer, mock_tts_engine)
        await vm.set_voice_mode(True)
        assert not vm._state.enabled
        mock_ws.send.assert_called_with("voice_status", {
            "status": "error",
            "error": "Microphone not available",
        })

    @pytest.mark.asyncio
    async def test_disable_voice_mode(self, voice_module, mock_ws):
        voice_module._state.enabled = True
        await voice_module.set_voice_mode(False)
        assert not voice_module._state.enabled
        mock_ws.send.assert_called_with("voice_status", {"status": "toggled", "enabled": False})


class TestTTS:
    @pytest.mark.asyncio
    async def test_speak_emits_status_events(self, voice_module, mock_ws):
        voice_module._state.enabled = True
        await voice_module.speak("Hello world")
        calls = [c.args for c in mock_ws.send.call_args_list]
        assert ("voice_status", {"status": "speaking_start"}) in calls
        assert ("voice_status", {"status": "speaking_end"}) in calls

    @pytest.mark.asyncio
    async def test_speak_skipped_when_voice_disabled(self, voice_module, mock_ws, mock_tts_engine):
        voice_module._state.enabled = False
        await voice_module.speak("Hello")
        mock_tts_engine.say.assert_not_called()

    @pytest.mark.asyncio
    async def test_speak_calls_tts_engine(self, voice_module, mock_tts_engine):
        voice_module._state.enabled = True
        await voice_module.speak("Test speech")
        mock_tts_engine.say.assert_called_once_with("Test speech")
        mock_tts_engine.runAndWait.assert_called_once()


class TestSTT:
    def test_capture_returns_transcribed_text(self, voice_module, mock_recognizer):
        mock_recognizer.recognize_google.return_value = "open notepad"
        result = voice_module._capture_and_transcribe()
        assert result == "open notepad"

    def test_capture_returns_none_on_timeout(self, voice_module, mock_recognizer):
        mock_recognizer.listen.side_effect = sr.WaitTimeoutError()
        result = voice_module._capture_and_transcribe()
        assert result is None

    def test_capture_returns_none_on_unknown_value(self, voice_module, mock_recognizer):
        mock_recognizer.recognize_google.side_effect = sr.UnknownValueError()
        with patch("asyncio.run_coroutine_threadsafe"):
            result = voice_module._capture_and_transcribe()
        assert result is None
