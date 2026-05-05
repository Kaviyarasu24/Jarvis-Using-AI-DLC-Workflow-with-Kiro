# Unit 1: UI Foundation — Business Rules

## Configuration Rules

| ID | Rule |
|---|---|
| BR-U1-001 | config.json MUST be loaded before any module initializes |
| BR-U1-002 | Missing config.json SHALL use default values — application must not crash on missing config |
| BR-U1-003 | Environment variables SHALL override config.json values (e.g. `OLLAMA_MODEL`, `BACKEND_PORT`) |
| BR-U1-004 | The `data/` directory SHALL be created automatically on startup if it does not exist |
| BR-U1-005 | `conversation_history.json` and `tasks.json` SHALL be created with empty structures if they do not exist |

## WebSocket Rules

| ID | Rule |
|---|---|
| BR-U1-010 | Every WebSocket message MUST use the envelope format: `{ type, payload, timestamp }` |
| BR-U1-011 | The backend MUST accept only one active WebSocket connection at a time (single-user app) |
| BR-U1-012 | On WebSocket disconnect, the backend MUST clean up the connection without crashing |
| BR-U1-013 | The frontend MUST attempt to reconnect automatically if the WebSocket connection drops |
| BR-U1-014 | Unknown message types received by either side MUST be logged and silently ignored (no crash) |

## Frontend Layout Rules

| ID | Rule |
|---|---|
| BR-U1-020 | The single-page layout MUST render: NotificationBar (top), ChatPanel (center), StatsSidebar (right) |
| BR-U1-021 | The CalendarPanel MUST be accessible via a toggle button — hidden by default |
| BR-U1-022 | The layout MUST be responsive — usable at minimum 1024px wide |
| BR-U1-023 | All placeholder components MUST render without errors even with null/empty data |
| BR-U1-024 | The frontend MUST display a connection status indicator (connected / disconnected) |

## Startup Sequence Rules

| ID | Rule |
|---|---|
| BR-U1-030 | Backend startup order: ConfigManager → data directory init → WebSocketManager → FastAPI routes → server start |
| BR-U1-031 | Frontend startup: establish WebSocket connection on App mount |
| BR-U1-032 | If backend is unreachable on frontend load, display a clear "Connecting..." state — do not show blank screen |

## CORS Rules

| ID | Rule |
|---|---|
| BR-U1-040 | FastAPI MUST allow CORS from the React dev server origin (localhost:5173) during development |
| BR-U1-041 | In production build, React is served as static files from FastAPI — CORS not required |
