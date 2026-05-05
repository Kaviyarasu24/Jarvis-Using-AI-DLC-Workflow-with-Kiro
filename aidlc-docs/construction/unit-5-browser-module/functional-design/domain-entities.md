# Unit 5: Browser Module — Domain Entities

## BrowserResult
Result of a web search or URL fetch operation.

```
BrowserResult
├── success: bool
├── query: str              — original search query
├── summary: str            — AI-summarized content
├── sources: list[str]      — source URLs found
└── error: str | None
```

## SearchIntent
Parsed search intent from user message.

```
SearchIntent
├── query: str              — extracted search query
└── is_url: bool            — True if user provided a direct URL
```
