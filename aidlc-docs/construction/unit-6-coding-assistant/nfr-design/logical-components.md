# Unit 6: Coding Assistant — Logical Components

| Component | Purpose |
|---|---|
| `CodingAssistant` | Task detection, system prompt selection, response parsing |
| `AICore` (Unit 3) | Ollama LLM calls with coding system prompt |
| `IntentRouter` (Unit 3) | Routes "code" intent to CodingAssistant |
| `react-syntax-highlighter` | Frontend code block rendering with syntax highlighting |
| `ChatPanel` (Unit 1) | Renders code messages with SyntaxHighlighter |
