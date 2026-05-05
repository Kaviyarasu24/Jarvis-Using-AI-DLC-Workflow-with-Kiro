# Unit 3: AI Core — Tech Stack Decisions

| Component | Choice | Rationale |
|---|---|---|
| LLM | Ollama local (llama3.2:3b) | User-specified; fully offline; no API key needed |
| HTTP client | `httpx` (async) | Already in requirements.txt; async-native; clean API |
| Ollama endpoint | `POST /api/chat` | Standard Ollama chat completions endpoint |
| History storage | JSON file (stdlib) | Simple, no database dependency, single-user |
| Atomic writes | Write to temp file + rename | Prevents corruption on unexpected shutdown |
