# Unit 1: UI Foundation — Code Generation Plan

## Unit Context
- **Unit**: Unit 1 — UI Foundation
- **Type**: Greenfield multi-unit monolith
- **Code Location**: `jarvis/` (workspace root)
- **Backend**: `jarvis/backend/`
- **Frontend**: `jarvis/frontend/`
- **Data**: `jarvis/data/`

## Requirements Covered
FR-070, FR-071, FR-073 (shell), FR-074 (shell), FR-075 (shell)
NFR-023, NFR-030, NFR-031, NFR-032, NFR-042, NFR-050, NFR-051

## Dependencies
None — this is the foundation unit.

---

## Execution Steps

### Project Structure & Configuration

- [x] Step 1: Create project root directory structure (`jarvis/`, `jarvis/backend/`, `jarvis/frontend/`, `jarvis/data/`)
- [x] Step 2: Create `jarvis/config.json` — default application configuration
- [x] Step 3: Create `jarvis/requirements.txt` — Python backend dependencies
- [x] Step 4: Create `jarvis/backend/__init__.py` — package marker

### Backend — ConfigManager

- [x] Step 5: Create `jarvis/backend/config_manager.py` — config loading, env var overrides, typed properties

### Backend — WebSocketManager

- [x] Step 6: Create `jarvis/backend/websocket_manager.py` — connection management, send/broadcast, message envelope

### Backend — Main FastAPI App

- [x] Step 7: Create `jarvis/backend/main.py` — FastAPI app, lifespan, CORS, WebSocket route, REST health endpoint, echo handler

### Backend — Data Initializer

- [x] Step 8: Create `jarvis/backend/data_init.py` — ensure data/ dir and JSON files exist on startup

### Backend — Tests

- [x] Step 9: Create `jarvis/backend/tests/__init__.py`
- [x] Step 10: Create `jarvis/backend/tests/test_config_manager.py` — unit tests for ConfigManager
- [x] Step 11: Create `jarvis/backend/tests/test_websocket_manager.py` — unit tests for WebSocketManager

### Frontend — Project Setup

- [x] Step 12: Create `jarvis/frontend/package.json` — React + TypeScript + Vite + Tailwind dependencies
- [x] Step 13: Create `jarvis/frontend/tsconfig.json` — TypeScript strict config
- [x] Step 14: Create `jarvis/frontend/vite.config.ts` — Vite config with WS proxy to FastAPI
- [x] Step 15: Create `jarvis/frontend/index.html` — Vite entry HTML
- [x] Step 16: Create `jarvis/frontend/tailwind.config.js` — Tailwind dark theme config
- [x] Step 17: Create `jarvis/frontend/postcss.config.js` — PostCSS for Tailwind

### Frontend — Types & Context

- [x] Step 18: Create `jarvis/frontend/src/types/index.ts` — all shared TypeScript interfaces
- [x] Step 19: Create `jarvis/frontend/src/context/WebSocketContext.tsx` — WS context, provider, useWebSocket hook

### Frontend — Components

- [x] Step 20: Create `jarvis/frontend/src/components/NotificationBar.tsx` — notification bar (empty state)
- [x] Step 21: Create `jarvis/frontend/src/components/VoiceIndicator.tsx` — disabled mic placeholder
- [x] Step 22: Create `jarvis/frontend/src/components/StatsSidebar.tsx` — stats sidebar skeleton
- [x] Step 23: Create `jarvis/frontend/src/components/CalendarPanel.tsx` — calendar placeholder
- [x] Step 24: Create `jarvis/frontend/src/components/ChatPanel.tsx` — full chat UI (echo mode)

### Frontend — App Root & Styles

- [x] Step 25: Create `jarvis/frontend/src/App.tsx` — root component, layout, WS init, global state
- [x] Step 26: Create `jarvis/frontend/src/main.tsx` — React entry point
- [x] Step 27: Create `jarvis/frontend/src/index.css` — global styles, dark theme base

### Documentation

- [x] Step 28: Create `jarvis/README.md` — project overview, setup instructions, run commands
- [x] Step 29: Create `aidlc-docs/construction/unit-1-ui-foundation/code/code-summary.md` — code summary

---

## Total Steps: 29
