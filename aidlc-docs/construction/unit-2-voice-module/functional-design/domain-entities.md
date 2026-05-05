# Unit 2: Voice Module — Domain Entities

## Core Entities

### VoiceMode
Represents the current voice interaction state.

```
VoiceMode
├── enabled: bool          — whether voice mode is active
├── listening: bool        — microphone is actively capturing
├── speaking: bool         — TTS is currently speaking
└── available: bool        — microphone hardware is accessible
```

### TranscriptionResult
Result of a speech-to-text operation.

```
TranscriptionResult
├── success: bool
├── text: str | None       — transcribed text (None on failure)
└── error: str | None      — error message if failed
```

### VoiceStatusEvent
WebSocket event emitted during voice pipeline transitions.

```
VoiceStatusEvent
├── status: VoiceStatus    — "listening_start" | "listening_end" | "speaking_start" | "speaking_end" | "toggled" | "error"
├── enabled: bool | None   — current voice mode state (for "toggled" events)
└── error: str | None      — error detail (for "error" events)
```

### VoiceConfig (from ConfigManager)
Voice-relevant configuration values.

```
VoiceConfig
├── voice_timeout_seconds: int     — max seconds to wait for speech (default: 5)
├── voice_phrase_limit: int        — max phrase duration in seconds (default: 10)
└── tts_rate: int                  — TTS speech rate words-per-minute (default: 175)
```
