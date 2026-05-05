# Unit 3: AI Core — Logical Components

| Component | Purpose |
|---|---|
| `AICore` | Ollama chat, history management, context window |
| `IntentRouter` | LLM-based classification + handler dispatch |
| `ConversationHistory` | In-memory list + JSON persistence |
| `httpx.AsyncClient` | Async HTTP to Ollama REST API |
| `data/conversation_history.json` | Persistent storage |
| `WebSocketManager` (Unit 1) | Sends chat_response to frontend |
| `VoiceModule` (Unit 2) | Speaks AI responses when voice mode active |
