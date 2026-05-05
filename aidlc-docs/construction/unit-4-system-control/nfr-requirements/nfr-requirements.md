# Unit 4: System Control & Monitoring — NFR Requirements

## Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-U4-P01 | System stats refresh interval | Configurable, default 5s |
| NFR-U4-P02 | Battery/network poll interval | Configurable, default 10s |
| NFR-U4-P03 | Shell command execution timeout | 30 seconds |
| NFR-U4-P04 | Monitoring loop MUST NOT block the asyncio event loop | Run psutil in executor |

## Reliability

| ID | Requirement |
|---|---|
| NFR-U4-R01 | psutil errors (e.g. no battery on desktop) MUST be handled gracefully — return None |
| NFR-U4-R02 | Shell command failures MUST return error output — not crash the backend |
| NFR-U4-R03 | Monitoring loop MUST restart automatically if it crashes |
| NFR-U4-R04 | Pending confirmations MUST expire after 60 seconds |

## Security (Basic)

| ID | Requirement |
|---|---|
| NFR-U4-S01 | File deletion and shell commands MUST require explicit confirmation |
| NFR-U4-S02 | Shell commands MUST run with the same privileges as the JARVIS process |
