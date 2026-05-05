# Unit 3: AI Core — Domain Entities

## ConversationMessage
A single message in the conversation history.

```
ConversationMessage
├── role: str          — "user" | "assistant" | "system"
├── content: str       — message text
└── timestamp: str     — ISO 8601
```

## ConversationHistory
The full persisted conversation history.

```
ConversationHistory
└── messages: list[ConversationMessage]
```

## OllamaRequest
Payload sent to the Ollama /api/chat endpoint.

```
OllamaRequest
├── model: str
├── messages: list[{ role, content }]
└── stream: bool
```

## OllamaResponse
Response from Ollama /api/chat.

```
OllamaResponse
├── message: { role: str, content: str }
└── done: bool
```

## IntentClassification
Result of LLM-based intent classification.

```
IntentClassification
├── intent: str    — "chat" | "code" | "search" | "system" | "calendar" | "voice_control"
└── confidence: str  — "high" | "low" (for logging)
```

## ChatResponse
Structured response returned to the WebSocket layer.

```
ChatResponse
├── text: str
├── message_type: str   — "text" | "code"
└── language: str | None
```
