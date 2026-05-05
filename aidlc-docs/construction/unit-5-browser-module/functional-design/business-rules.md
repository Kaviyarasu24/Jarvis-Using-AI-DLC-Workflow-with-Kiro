# Unit 5: Browser Module — Business Rules

| ID | Rule |
|---|---|
| BR-U5-001 | Web search SHALL be triggered by user intent keywords: "search for", "find", "look up", "what is", "who is", "how to", "browse" |
| BR-U5-002 | The `browser-use` framework SHALL be used for AI-native web search and content extraction |
| BR-U5-003 | Search results SHALL be summarized by the Ollama model before returning to the user |
| BR-U5-004 | Source URLs SHALL be included in the response |
| BR-U5-005 | If `browser-use` fails, a clear error message SHALL be returned — no crash |
| BR-U5-006 | Browser operations SHALL run in a thread executor to avoid blocking asyncio |
| BR-U5-007 | Search timeout SHALL be 60 seconds |
