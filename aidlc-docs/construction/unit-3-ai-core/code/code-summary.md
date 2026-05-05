# Unit 3: AI Core — Code Summary

## Files Created / Modified

| File | Action | Purpose |
|---|---|---|
| `jarvis/backend/ai_core.py` | Created | Ollama integration, conversation history, intent classification |
| `jarvis/backend/intent_router.py` | Created | LLM-based intent classification + handler dispatch |
| `jarvis/backend/main.py` | Modified | Wired AICore + IntentRouter, replaced echo with real routing, clear_history |
| `jarvis/backend/tests/test_ai_core.py` | Created | 13 unit tests (history, chat, Ollama errors, intent classification) |
| `jarvis/backend/tests/test_intent_router.py` | Created | 4 unit tests (routing, fallback, error handling, registration) |

## Requirements Covered
FR-001, FR-002, FR-003, FR-004, FR-005
NFR-001, NFR-010, NFR-013

## Key Design Decisions
- Atomic JSON write (tmp + rename) prevents history corruption
- Intent classification uses a short context (no history) for speed
- Unknown intents default to "chat" — never crash
- All Ollama errors return user-friendly messages
- HTTP client injectable for testing (no real Ollama needed in tests)
