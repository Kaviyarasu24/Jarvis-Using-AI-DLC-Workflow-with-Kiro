# JARVIS Unit of Work — Dependency Matrix

## Dependency Overview

| Unit | Name | Depends On | Blocks |
|---|---|---|---|
| Unit 1 | UI Foundation | — (no dependencies) | Units 2, 3, 4, 5, 6, 7 |
| Unit 2 | Voice Module | Unit 1 | Unit 3 (TTS integration) |
| Unit 3 | AI Core | Unit 1, Unit 2 | Units 5, 6, 7 |
| Unit 4 | System Control & Monitoring | Unit 1, Unit 3 | — |
| Unit 5 | Browser Module | Unit 1, Unit 3 | — |
| Unit 6 | Coding Assistant | Unit 1, Unit 3 | — |
| Unit 7 | Calendar & Tasks | Unit 1, Unit 3 | — |

---

## Dependency Detail

### Unit 1 → All Units
Unit 1 provides the foundational infrastructure every other unit requires:
- `WebSocketManager` — all backend modules emit events through it
- `ConfigManager` — all modules read configuration from it
- FastAPI app instance — all REST endpoints and WebSocket route registered here
- React frontend shell — all frontend components are placeholders until their unit is built

### Unit 2 → Unit 3
Unit 2 (VoiceModule) must be built before Unit 3 is fully wired because:
- Unit 3 (AI Core) calls `VoiceModule.speak()` to read AI responses aloud when voice mode is active
- The voice status WebSocket events (`speaking_start/end`) are emitted during AI response delivery

### Unit 3 → Units 4, 5, 6, 7
Unit 3 (IntentRouter) is the central dispatcher. Units 4–7 each register a handler with IntentRouter:
- Unit 4 registers `system_controller` and `calendar` handlers
- Unit 5 registers `browser` handler
- Unit 6 registers `code` handler
- Unit 7 registers `calendar` handler (CalendarManager)

Without Unit 3, there is no routing mechanism to reach any of these modules.

---

## Development Sequence

```
Unit 1 (UI Foundation)
    |
    +──> Unit 2 (Voice Module)
              |
              +──> Unit 3 (AI Core)
                        |
                        +──> Unit 4 (System Control & Monitoring)  [parallel]
                        |
                        +──> Unit 5 (Browser Module)               [parallel]
                        |
                        +──> Unit 6 (Coding Assistant)             [parallel]
                        |
                        +──> Unit 7 (Calendar & Tasks)             [parallel]
```

**Sequential**: Units 1 → 2 → 3 must be built in order (hard dependencies)

**Parallel opportunity**: Units 4, 5, 6, 7 can theoretically be developed in parallel after Unit 3, but per user priority order they are developed sequentially: 4 → 5 → 6 → 7

---

## Shared Component Evolution

Some frontend components are built as shells in Unit 1 and enhanced in later units:

| Component | Unit 1 | Enhanced In |
|---|---|---|
| `ChatPanel.tsx` | Shell (echo display) | Unit 3 (AI logic), Unit 6 (code highlight) |
| `VoiceIndicator.tsx` | Placeholder | Unit 2 (full waveform + toggle) |
| `StatsSidebar.tsx` | Placeholder | Unit 4 (live stats) |
| `NotificationBar.tsx` | Empty | Unit 4 (alerts) |
| `CalendarPanel.tsx` | Placeholder | Unit 7 (full task UI) |

---

## Integration Points

| Integration | Units Involved | Interface |
|---|---|---|
| Voice → AI response spoken | Unit 2 + Unit 3 | `VoiceModule.speak(ai_response_text)` |
| Intent routing to system | Unit 3 + Unit 4 | `IntentRouter` dispatches to `SystemController` |
| Intent routing to browser | Unit 3 + Unit 5 | `IntentRouter` dispatches to `BrowserModule` |
| Intent routing to coding | Unit 3 + Unit 6 | `IntentRouter` dispatches to `CodingAssistant` |
| Intent routing to calendar | Unit 3 + Unit 7 | `IntentRouter` dispatches to `CalendarManager` |
| System stats → UI | Unit 4 + Unit 1 | `SystemMonitor` → `WebSocketManager.broadcast(stats_update)` |
| Alerts → UI | Unit 4 + Unit 1 | `SystemMonitor` → `WebSocketManager.broadcast(alert)` |
| Calendar REST → UI | Unit 7 + Unit 1 | REST `/api/tasks*` → `CalendarPanel` fetch calls |
