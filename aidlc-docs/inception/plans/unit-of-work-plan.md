# JARVIS Unit of Work Plan

## Plan Overview
Decompose JARVIS into 7 development units based on the application design, requirements, and user-specified priority order.

---

## Execution Checklist

- [x] Step 1: Analyze application design and determine unit boundaries
- [x] Step 2: Generate `unit-of-work.md` — unit definitions and responsibilities
- [x] Step 3: Generate `unit-of-work-dependency.md` — dependency matrix
- [x] Step 4: Generate `unit-of-work-story-map.md` — requirements-to-unit mapping
- [x] Step 5: Validate unit boundaries and completeness

---

## Unit Decomposition Analysis

### Decomposition Rationale
- Each unit maps to one primary backend module + related frontend component(s)
- Units are ordered by user-specified priority: UI → Voice → AI Core → System → Browser → Coding → Calendar
- Units 1–3 form the core foundation; Units 4–7 are additive capabilities
- Unit 1 (UI) must be built first as it provides the shell all other units plug into
- Unit 3 (AI Core) must precede Units 5 and 6 (Browser, Coding) as they depend on AICore
- All other units are independently developable after Unit 1

### Deployment Model
Single deployable application — Python backend + React frontend served together. No microservices. Units are logical modules within one codebase.

---

## Units Summary

| # | Unit | Backend Module(s) | Frontend Component(s) | Priority |
|---|---|---|---|---|
| 1 | UI Foundation | `main.py`, `websocket_manager.py`, `config_manager.py` | All React components (shell) | 1 |
| 2 | Voice Module | `voice_module.py` | `VoiceIndicator.tsx` | 2 |
| 3 | AI Core | `ai_core.py`, `intent_router.py` | `ChatPanel.tsx` (chat logic) | 3 |
| 4 | System Control | `system_controller.py`, `system_monitor.py` | `StatsSidebar.tsx`, `NotificationBar.tsx` | 4 |
| 5 | Browser Module | `browser_module.py` | — (chat response only) | 5 |
| 6 | Coding Assistant | `coding_assistant.py` | Code block rendering in `ChatPanel.tsx` | 6 |
| 7 | Calendar & Tasks | `calendar_manager.py` | `CalendarPanel.tsx` | 7 |
