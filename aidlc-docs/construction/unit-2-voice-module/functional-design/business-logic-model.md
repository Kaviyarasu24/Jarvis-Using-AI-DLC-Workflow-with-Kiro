# Unit 2: Voice Module — Business Logic Model

## 1. Voice Mode Toggle Logic

```
ON receive voice_toggle(enabled=True):
  IF microphone not available:
    emit voice_status("error", error="Microphone not available")
    RETURN
  SET voice_mode.enabled = True
  emit voice_status("toggled", enabled=True)
  START listening loop (async task)

ON receive voice_toggle(enabled=False):
  SET voice_mode.enabled = False
  STOP any active listening
  emit voice_status("toggled", enabled=False)
```

## 2. Listening Loop

```
WHILE voice_mode.enabled:
  IF voice_mode.speaking: WAIT (don't listen while speaking)
  
  emit voice_status("listening_start")
  SET voice_mode.listening = True
  
  TRY:
    audio = microphone.listen(timeout=config.voice_timeout_seconds,
                              phrase_time_limit=config.voice_phrase_limit)
    text = recognizer.recognize_google(audio)
    emit voice_status("listening_end")
    SET voice_mode.listening = False
    
    IF text is not empty:
      → pass text to IntentRouter (same pipeline as text input)
  
  EXCEPT WaitTimeoutError:
    emit voice_status("listening_end")
    SET voice_mode.listening = False
    CONTINUE loop (timeout is normal — just try again)
  
  EXCEPT UnknownValueError:
    emit voice_status("listening_end")
    SET voice_mode.listening = False
    send chat_response("I didn't catch that. Please try again.")
    CONTINUE loop
  
  EXCEPT RequestError as e:
    emit voice_status("error", error=str(e))
    SET voice_mode.listening = False
    send chat_response("Speech recognition service unavailable.")
    BREAK loop (disable voice mode)
```

## 3. Text-to-Speech Logic

```
FUNCTION speak(text: str):
  IF NOT voice_mode.enabled: RETURN
  IF NOT tts_available: RETURN
  
  SET voice_mode.speaking = True
  emit voice_status("speaking_start")
  
  RUN in background thread:
    engine.say(text)
    engine.runAndWait()
  
  AWAIT thread completion
  SET voice_mode.speaking = False
  emit voice_status("speaking_end")
```

## 4. Availability Check

```
FUNCTION check_microphone_available() -> bool:
  TRY:
    with Microphone() as source:
      recognizer.adjust_for_ambient_noise(source, duration=0.1)
    RETURN True
  EXCEPT (OSError, AttributeError):
    RETURN False

FUNCTION check_tts_available() -> bool:
  TRY:
    engine = pyttsx3.init()
    RETURN True
  EXCEPT Exception:
    RETURN False
```

## 5. Integration with Chat Pipeline (Unit 3 dependency)

In Unit 2, transcribed text is forwarded to the WebSocket pipeline as a `user_message`. When Unit 3 (AI Core) is integrated, the response text is passed back to `VoiceModule.speak()` if voice mode is active.

```
Transcribed text
      |
      v
ws_manager.send("user_message", { text: transcribed_text })
      |
      v
[Unit 3 processes and returns chat_response]
      |
      v
IF voice_mode.enabled:
  VoiceModule.speak(response_text)
```
