# Unit 6: Coding Assistant — Business Rules

| ID | Rule |
|---|---|
| BR-U6-001 | All coding assistance SHALL use the same Ollama model (llama3.2:3b) with a coding-specific system prompt |
| BR-U6-002 | The coding task type SHALL be detected from the user message before calling Ollama |
| BR-U6-003 | Task type detection SHALL use keyword matching: generate/write/create → "generate", explain/what does → "explain", debug/fix/error → "debug", refactor/improve/clean → "refactor", review/check/audit → "review" |
| BR-U6-004 | Code responses SHALL be rendered with syntax highlighting in the frontend (message_type="code") |
| BR-U6-005 | The response SHALL include both the code block AND an explanation |
| BR-U6-006 | JARVIS SHALL NOT execute generated code (FR-024) |
| BR-U6-007 | If no code block is detected in the response, the full response SHALL be returned as plain text |
| BR-U6-008 | The detected programming language SHALL be included in the response for syntax highlighting |
