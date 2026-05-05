# Unit 5: Browser Module — Tech Stack Decisions

| Component | Choice | Rationale |
|---|---|---|
| Browser automation | `browser-use` 0.1.40 | User-specified; AI-native; integrates with LLM for intelligent extraction |
| LLM for browser-use | Ollama (llama3.2:3b) | Same model used throughout; no extra API key |
| Async bridge | `asyncio.run_in_executor` | browser-use may block; run off event loop |
| Result summarization | AICore.chat() | Reuse existing Ollama integration |

## Note on browser-use + Ollama
`browser-use` natively supports Ollama via `langchain-ollama`. The agent uses the same local model to decide what to click, extract, and summarize.
