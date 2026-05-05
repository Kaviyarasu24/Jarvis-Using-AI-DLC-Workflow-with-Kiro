# Unit 3: AI Core — Business Logic Model

## 1. Message Processing Pipeline

```
User message arrives (WebSocket: user_message or user_message_from_voice)
      |
      v
IntentRouter.route(message)
      |
      +-- classify_intent(message) --> Ollama (short prompt)
      |         returns: "chat" | "code" | "search" | "system" | "calendar" | "voice_control"
      |
      +-- dispatch to handler:
            "chat"          --> AICore.chat(message)
            "voice_control" --> VoiceModule.set_voice_mode(...)
            others          --> AICore.chat(message)  [fallback until Units 4-7]
      |
      v
ChatResponse { text, message_type, language? }
      |
      v
WebSocketManager.send("chat_response", payload)
      |
      v  [if voice mode enabled]
VoiceModule.speak(response_text)
```

## 2. Intent Classification Logic

```
FUNCTION classify_intent(message: str) -> str:
  classification_prompt = """
  Classify the following user message into exactly one category.
  Respond with ONLY the category name, nothing else.
  Categories: chat, code, search, system, calendar, voice_control
  
  Rules:
  - chat: general conversation, questions, explanations
  - code: anything about writing, debugging, explaining, or reviewing code
  - search: requests to search the web or find online information
  - system: file operations, launching apps, running commands, OS control
  - calendar: tasks, reminders, scheduling, to-do items
  - voice_control: turn on/off voice, enable/disable microphone
  
  Message: {message}
  """
  
  response = ollama_request(
    model=config.ollama_model,
    messages=[{ "role": "user", "content": classification_prompt }],
    system=None
  )
  
  intent = response.strip().lower()
  VALID_INTENTS = {"chat", "code", "search", "system", "calendar", "voice_control"}
  
  IF intent not in VALID_INTENTS:
    log warning: f"Unknown intent '{intent}', defaulting to 'chat'"
    RETURN "chat"
  
  RETURN intent
```

## 3. AICore Chat Logic

```
FUNCTION chat(message: str, system_prompt: str = JARVIS_SYSTEM_PROMPT) -> str:
  # Append user message to history
  history.append({ role: "user", content: message, timestamp: now() })
  
  # Build context window (last N messages)
  context = history.get_context_window(config.history_context_window)
  
  # Call Ollama
  TRY:
    response_text = ollama_chat(
      model=config.ollama_model,
      messages=context,
      system=system_prompt
    )
  EXCEPT OllamaUnavailable:
    RETURN "I'm having trouble connecting to my AI engine. Please make sure Ollama is running."
  EXCEPT TimeoutError:
    RETURN "The response took too long. Please try again."
  
  # Append assistant response to history
  history.append({ role: "assistant", content: response_text, timestamp: now() })
  
  # Persist history
  history.save()
  
  RETURN response_text
```

## 4. Conversation History Persistence

```
ON startup:
  IF data/conversation_history.json exists AND has messages:
    Load messages into memory
  ELSE:
    Initialize empty history

ON each assistant response:
  Append to in-memory list
  Write entire list to data/conversation_history.json (atomic write)

ON clear_history command:
  Clear in-memory list
  Write { "messages": [] } to data/conversation_history.json
```

## 5. JARVIS System Prompt

```
JARVIS_SYSTEM_PROMPT = """
You are JARVIS, an intelligent AI-powered personal assistant.
You help with general questions, coding, web searches, system tasks, and scheduling.
Be concise, helpful, and friendly. When you don't know something, say so clearly.
"""
```
