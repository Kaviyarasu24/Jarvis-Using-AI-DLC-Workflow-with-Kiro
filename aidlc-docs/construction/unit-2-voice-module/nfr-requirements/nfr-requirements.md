# Unit 2: Voice Module — NFR Requirements

## Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-U2-P01 | Voice recognition processing time after speech ends | < 2 seconds (FR-NFR-002) |
| NFR-U2-P02 | TTS must not block the asyncio event loop | Run in background thread |
| NFR-U2-P03 | Voice status WebSocket events must be emitted within 50ms of state change | < 50ms |

## Reliability

| ID | Requirement |
|---|---|
| NFR-U2-R01 | Microphone unavailability MUST NOT crash the application |
| NFR-U2-R02 | STT timeout (no speech detected) MUST be handled gracefully — loop continues |
| NFR-U2-R03 | STT API errors MUST disable voice mode gracefully with user notification |
| NFR-U2-R04 | pyttsx3 initialization failure MUST be caught — TTS silently disabled |
| NFR-U2-R05 | Voice module MUST be independently testable with mocked audio I/O |

## Usability

| ID | Requirement |
|---|---|
| NFR-U2-U01 | Voice mode state MUST be clearly visible in the UI at all times |
| NFR-U2-U02 | Listening and speaking states MUST have distinct visual indicators |
| NFR-U2-U03 | Microphone unavailability MUST be communicated to the user via disabled button state |

## Maintainability

| ID | Requirement |
|---|---|
| NFR-U2-M01 | All audio I/O operations MUST be isolated in `voice_module.py` — no audio code elsewhere |
| NFR-U2-M02 | Voice config values (timeout, rate) MUST come from ConfigManager |
| NFR-U2-M03 | VoiceModule MUST be mockable for unit testing (injectable recognizer and engine) |
