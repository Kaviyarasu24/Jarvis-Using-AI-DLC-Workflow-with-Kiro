# Unit 6: Coding Assistant — Tech Stack Decisions

| Component | Choice | Rationale |
|---|---|---|
| LLM | Ollama llama3.2:3b | User-specified; same model throughout |
| Code parsing | Python `re` (stdlib) | Simple regex for markdown code block extraction |
| Syntax highlighting | `react-syntax-highlighter` (npm) | Standard React library for code rendering |
| Theme | `atomDark` (react-syntax-highlighter) | Matches JARVIS dark theme |
