# Unit 2: Voice Module — Logical Components

## Backend

| Component | Type | Purpose |
|---|---|---|
| `VoiceModule` | Python class | Orchestrates STT + TTS + state management |
| `sr.Recognizer` | External (speech_recognition) | Audio capture and transcription |
| `sr.Microphone` | External (speech_recognition/PyAudio) | Microphone hardware access |
| `pyttsx3.Engine` | External (pyttsx3) | Text-to-speech synthesis |
| `threading.Thread` / executor | Python stdlib | Isolates blocking TTS from asyncio |
| `WebSocketManager` | Unit 1 dependency | Emits voice status events to frontend |
| `ConfigManager` | Unit 1 dependency | Provides voice timeout and TTS rate config |

## Frontend

| Component | Type | Purpose |
|---|---|---|
| `VoiceIndicator` | React component | Visual voice state display + toggle button |
| `WebSocketContext` | Unit 1 dependency | Receives `voice_status` events, sends `voice_toggle` |

## No External Services
Voice processing is entirely local:
- STT: Google Web Speech API (requires internet) — fallback: offline recognizer if needed
- TTS: Windows SAPI5 via pyttsx3 (fully offline)
