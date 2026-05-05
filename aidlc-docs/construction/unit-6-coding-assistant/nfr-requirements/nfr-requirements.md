# Unit 6: Coding Assistant — NFR Requirements

## Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-U6-P01 | Coding response latency (local Ollama) | < 15s for typical code generation |

## Reliability

| ID | Requirement |
|---|---|
| NFR-U6-R01 | Ollama errors MUST be handled gracefully (inherited from AICore) |
| NFR-U6-R02 | Malformed responses (no code block) MUST fall back to plain text |

## Usability

| ID | Requirement |
|---|---|
| NFR-U6-U01 | Code blocks MUST be rendered with syntax highlighting in the frontend |
| NFR-U6-U02 | Language MUST be detected and passed to the frontend for correct highlighting |
