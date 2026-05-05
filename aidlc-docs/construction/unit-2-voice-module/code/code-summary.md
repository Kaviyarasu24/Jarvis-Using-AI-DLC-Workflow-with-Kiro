# Unit 2: Voice Module — Code Summary

## Files Created / Modified

| File | Action | Purpose |
|---|---|---|
| `jarvis/config.json` | Modified | Added voice_timeout_seconds, voice_phrase_limit_seconds, tts_rate |
| `jarvis/backend/config_manager.py` | Modified | Added voice_timeout_seconds, voice_phrase_limit_seconds, tts_rate properties |
| `jarvis/backend/voice_module.py` | Created | Full STT + TTS + state management + WebSocket events |
| `jarvis/backend/main.py` | Modified | Wired VoiceModule, updated voice_toggle handler, health endpoint |
| `jarvis/backend/tests/test_voice_module.py` | Created | 14 unit tests (init, toggle, TTS, STT) |
| `jarvis/frontend/src/components/VoiceIndicator.tsx` | Modified | Full implementation: toggle button, waveform, speaking indicator |
| `jarvis/frontend/src/index.css` | Modified | Added waveform-bar animation keyframes |

## Requirements Covered
FR-010, FR-011, FR-012, FR-013, FR-014
NFR-002, NFR-011, NFR-021

## Test Coverage
- 14 tests: init (mic available/unavailable), voice toggle (enable/disable/mic unavailable), TTS (events, skip when disabled, engine calls), STT (transcription, timeout, unknown value)
