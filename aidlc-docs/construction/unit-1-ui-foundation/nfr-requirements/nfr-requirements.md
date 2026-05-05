# Unit 1: UI Foundation — NFR Requirements

## Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-U1-P01 | Application startup time (backend ready to accept connections) | < 5 seconds |
| NFR-U1-P02 | WebSocket connection establishment time | < 500ms |
| NFR-U1-P03 | Frontend initial page load time | < 2 seconds |
| NFR-U1-P04 | UI re-render on incoming WebSocket message | < 100ms |
| NFR-U1-P05 | Config file load time | < 100ms |

## Reliability

| ID | Requirement |
|---|---|
| NFR-U1-R01 | Backend MUST NOT crash on malformed WebSocket messages — log and continue |
| NFR-U1-R02 | Backend MUST NOT crash if config.json is missing — use defaults |
| NFR-U1-R03 | Frontend MUST auto-reconnect WebSocket on disconnect (max 5 retries, exponential backoff) |
| NFR-U1-R04 | Frontend MUST display a clear disconnected state — never show stale "connected" status |
| NFR-U1-R05 | Data directory and JSON files MUST be created automatically — no manual setup required |

## Usability

| ID | Requirement |
|---|---|
| NFR-U1-U01 | UI MUST be usable at 1024px minimum width |
| NFR-U1-U02 | Connection status MUST be visible at all times |
| NFR-U1-U03 | Placeholder components MUST render gracefully with no data (no blank screens, no errors) |
| NFR-U1-U04 | Dark theme applied consistently across all components |
| NFR-U1-U05 | Chat input MUST support Enter to send (Shift+Enter for newline) |

## Maintainability

| ID | Requirement |
|---|---|
| NFR-U1-M01 | All TypeScript types defined in `types/index.ts` — no inline type definitions in components |
| NFR-U1-M02 | WebSocket logic encapsulated in WebSocketContext — components do not manage raw WebSocket |
| NFR-U1-M03 | Config values accessed only through ConfigManager — no direct file reads in other modules |
| NFR-U1-M04 | Backend modules imported and initialized only in `main.py` — no circular imports |

## Security (Basic)

| ID | Requirement |
|---|---|
| NFR-U1-S01 | Backend port configurable — not hardcoded |
| NFR-U1-S02 | CORS restricted to localhost origins only |
| NFR-U1-S03 | No credentials or secrets in frontend code or config.json |
