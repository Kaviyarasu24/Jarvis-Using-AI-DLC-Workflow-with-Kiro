# Unit 4: System Control & Monitoring — Code Summary

## Files Created / Modified

| File | Action | Purpose |
|---|---|---|
| `jarvis/backend/system_controller.py` | Created | OS operations, NL command parser, confirmation gate |
| `jarvis/backend/system_monitor.py` | Created | psutil polling loop, stats broadcast, alert detection |
| `jarvis/backend/main.py` | Modified | Wired SystemController + SystemMonitor, confirm_action handler |
| `jarvis/backend/tests/test_system_controller.py` | Created | 14 tests (file ops, destructive confirmation, alert detection) |
| `jarvis/frontend/src/components/ChatPanel.tsx` | Modified | Added confirmation dialog UI (confirm/cancel buttons) |

## Requirements Covered
FR-040 to FR-055 (15 FRs), NFR-003, NFR-004, NFR-041

## Key Design Decisions
- Transition-based alerts: fire only on state change, not continuously
- Confirmation gate: two-phase (pending → confirm) with 60s TTL
- psutil + subprocess run in executor to avoid blocking asyncio
- Auto-restart monitoring loop on unexpected errors
- NL command parser handles common patterns; falls back gracefully
