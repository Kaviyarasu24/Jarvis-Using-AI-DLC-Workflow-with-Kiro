# Unit 2: Voice Module — Business Rules

## Voice Mode Rules

| ID | Rule |
|---|---|
| BR-U2-001 | Voice mode SHALL be disabled by default on application startup |
| BR-U2-002 | Voice mode toggle SHALL be triggered by a `voice_toggle` WebSocket message from the frontend |
| BR-U2-003 | If microphone is unavailable on toggle-on, voice mode SHALL NOT activate — emit error status and remain in text mode |
| BR-U2-004 | Voice mode state SHALL be emitted to the frontend via `voice_status` WebSocket message on every state change |

## Speech-to-Text Rules

| ID | Rule |
|---|---|
| BR-U2-010 | STT SHALL use the `speech_recognition` library with the default recognizer (Google Web Speech API) |
| BR-U2-011 | Listening SHALL begin only when voice mode is enabled and no TTS is currently speaking |
| BR-U2-012 | A `voice_status: "listening_start"` event SHALL be emitted before microphone capture begins |
| BR-U2-013 | A `voice_status: "listening_end"` event SHALL be emitted after transcription completes (success or failure) |
| BR-U2-014 | If transcription fails (timeout, unintelligible, API error), the error SHALL be logged and a friendly message sent to chat — voice mode remains active |
| BR-U2-015 | Transcribed text SHALL be passed directly to the intent routing pipeline (same as text input) |
| BR-U2-016 | Listening timeout SHALL be configurable (default: 5 seconds of silence) |

## Text-to-Speech Rules

| ID | Rule |
|---|---|
| BR-U2-020 | TTS SHALL use the `pyttsx3` library for offline speech synthesis |
| BR-U2-021 | TTS SHALL only speak when voice mode is enabled |
| BR-U2-022 | A `voice_status: "speaking_start"` event SHALL be emitted before TTS begins |
| BR-U2-023 | A `voice_status: "speaking_end"` event SHALL be emitted after TTS completes |
| BR-U2-024 | TTS SHALL run in a background thread to avoid blocking the asyncio event loop |
| BR-U2-025 | After TTS completes, if voice mode is still enabled, the next listening cycle SHALL begin automatically |
| BR-U2-026 | TTS speech rate SHALL be configurable (default: 175 wpm) |

## Availability Rules

| ID | Rule |
|---|---|
| BR-U2-030 | On startup, VoiceModule SHALL check microphone availability and log the result |
| BR-U2-031 | If microphone is unavailable, the frontend SHALL show the voice button as disabled |
| BR-U2-032 | Microphone unavailability SHALL NOT prevent the application from starting |
| BR-U2-033 | If pyttsx3 fails to initialize, TTS SHALL be silently disabled — text responses still work |
