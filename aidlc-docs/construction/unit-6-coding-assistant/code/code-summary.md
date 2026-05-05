# Unit 6: Coding Assistant — Code Summary

## Files Created / Modified

| File | Action | Purpose |
|---|---|---|
| `jarvis/backend/coding_assistant.py` | Created | Task detection, system prompts, code block extraction |
| `jarvis/backend/main.py` | Modified | Wired CodingAssistant, registered "code" intent handler |
| `jarvis/backend/tests/test_coding_assistant.py` | Created | 16 tests (task detection, code extraction, handle pipeline) |
| `jarvis/frontend/package.json` | Modified | Added react-syntax-highlighter + types |
| `jarvis/frontend/src/components/ChatPanel.tsx` | Modified | Code block rendering with SyntaxHighlighter + copy button |

## Requirements Covered
FR-020, FR-021, FR-022, FR-023, FR-024

## Key Design Decisions
- 5 task-specific system prompts for higher quality responses per task type
- Keyword-based task detection (fast, no LLM call needed)
- Code blocks rendered with react-syntax-highlighter (atomDark theme)
- Copy-to-clipboard button on every code block
- Falls back to plain text if no code block in response
