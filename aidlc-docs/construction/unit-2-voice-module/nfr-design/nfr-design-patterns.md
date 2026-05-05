# Unit 2: Voice Module — NFR Design Patterns

## 1. Thread Isolation Pattern (TTS)
pyttsx3 is synchronous and blocking. Running it on the asyncio event loop would freeze the entire backend.

```python
# Pattern: run blocking TTS in a thread pool executor
async def speak(self, text: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, self._speak_sync, text)

def _speak_sync(self, text: str) -> None:
    self._engine.say(text)
    self._engine.runAndWait()
```

## 2. Graceful Degradation Pattern
Each failure mode degrades gracefully without crashing:

```python
# Microphone unavailable → voice mode stays off
# STT timeout → loop continues silently
# STT API error → voice mode disabled, user notified
# TTS init failure → TTS disabled, text responses still work
```

## 3. Dependency Injection for Testability
Recognizer and engine are injected, not hardcoded:

```python
class VoiceModule:
    def __init__(self, config, ws_manager,
                 recognizer=None, tts_engine=None):
        self._recognizer = recognizer or sr.Recognizer()
        self._engine = tts_engine  # None = TTS disabled
```

## 4. State Machine Pattern
Voice pipeline follows a clear state machine:

```
IDLE
  |--[toggle on]--> LISTENING
  |                    |--[speech detected]--> PROCESSING --> SPEAKING --> LISTENING
  |                    |--[timeout]--> LISTENING (loop)
  |                    |--[API error]--> IDLE (disabled)
  |--[toggle off]--> IDLE
```
