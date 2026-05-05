# Unit 3: AI Core — NFR Requirements

## Performance

| ID | Requirement | Target |
|---|---|---|
| NFR-U3-P01 | AI response latency for typical queries (llama3.2:3b local) | < 10 seconds |
| NFR-U3-P02 | Intent classification latency (short prompt, no history) | < 3 seconds |
| NFR-U3-P03 | History file write after each response | < 100ms |

## Reliability

| ID | Requirement |
|---|---|
| NFR-U3-R01 | Ollama unavailability MUST return a friendly error message — no crash |
| NFR-U3-R02 | HTTP timeout to Ollama SHALL be set to 30 seconds |
| NFR-U3-R03 | Conversation history MUST NOT be lost on unexpected shutdown (write-on-update) |
| NFR-U3-R04 | Corrupted history JSON SHALL be handled gracefully — reset to empty history |

## Maintainability

| ID | Requirement |
|---|---|
| NFR-U3-M01 | AICore and IntentRouter MUST be independently testable with mocked HTTP client |
| NFR-U3-M02 | System prompts SHALL be defined as module-level constants — not inline strings |
| NFR-U3-M03 | Ollama HTTP calls SHALL be isolated in a single method for easy mocking |
