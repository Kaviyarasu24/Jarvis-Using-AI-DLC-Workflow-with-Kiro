# Unit 3: AI Core — Business Rules

## Conversation History Rules

| ID | Rule |
|---|---|
| BR-U3-001 | Conversation history SHALL be loaded from `data/conversation_history.json` on startup |
| BR-U3-002 | History SHALL be saved to JSON immediately after each assistant response (write-on-update) |
| BR-U3-003 | Only the last N messages (configurable, default 20) SHALL be included in the Ollama context window |
| BR-U3-004 | Both user and assistant messages SHALL be appended to history |
| BR-U3-005 | History clear command SHALL wipe in-memory history and overwrite the JSON file with empty structure |

## Intent Classification Rules

| ID | Rule |
|---|---|
| BR-U3-010 | Every incoming user message SHALL be classified by the Ollama model before routing |
| BR-U3-011 | The classification prompt SHALL instruct Ollama to respond with ONLY one of: chat, code, search, system, calendar, voice_control |
| BR-U3-012 | If classification response is not a recognized intent, default to "chat" |
| BR-U3-013 | Classification SHALL use a short context window (last 3 messages) to keep latency low |
| BR-U3-014 | Classification SHALL NOT be added to conversation history |

## Ollama Integration Rules

| ID | Rule |
|---|---|
| BR-U3-020 | All Ollama requests SHALL use the model specified in config (default: llama3.2:3b) |
| BR-U3-021 | If Ollama is unreachable, a clear error message SHALL be returned to the user — no crash |
| BR-U3-022 | Ollama requests SHALL include a system prompt appropriate to the intent (general vs coding) |
| BR-U3-023 | The general chat system prompt SHALL establish JARVIS persona |
| BR-U3-024 | Response timeout SHALL be handled gracefully with a user-facing error message |

## Routing Rules

| ID | Rule |
|---|---|
| BR-U3-030 | "chat" intent → AICore.chat() |
| BR-U3-031 | "code" intent → CodingAssistant.handle() (Unit 6 — falls back to chat in Unit 3) |
| BR-U3-032 | "search" intent → BrowserModule.search() (Unit 5 — falls back to chat in Unit 3) |
| BR-U3-033 | "system" intent → SystemController (Unit 4 — falls back to chat in Unit 3) |
| BR-U3-034 | "calendar" intent → CalendarManager (Unit 7 — falls back to chat in Unit 3) |
| BR-U3-035 | "voice_control" intent → VoiceModule.set_voice_mode() |
| BR-U3-036 | Unregistered handlers SHALL fall back to AICore.chat() |
