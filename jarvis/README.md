# JARVIS — AI-Powered Personal Assistant

JARVIS is a local AI personal assistant with voice interaction, coding assistance, browser automation, and system control — powered by Ollama (llama3.2:3b) and built with Python FastAPI + React TypeScript.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running locally
- Ollama model pulled: `ollama pull llama3.2:3b`
- Windows (primary target; Linux/macOS may work with minor adjustments)
- Microphone (for voice features)

---

## Project Structure

```
jarvis/
├── backend/          # Python FastAPI backend
├── frontend/         # React + TypeScript frontend
├── data/             # Auto-created: conversation_history.json, tasks.json
├── config.json       # Application configuration
└── requirements.txt  # Python dependencies
```

---

## Setup & Run

### 1. Backend

```bash
# From the jarvis/ directory
pip install -r requirements.txt

# Start the FastAPI backend
python -m backend.main
# Backend runs at http://localhost:8000
```

### 2. Frontend (Development)

```bash
# From the jarvis/frontend/ directory
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

Open `http://localhost:5173` in your browser.

### 3. Frontend (Production Build)

```bash
# From jarvis/frontend/
npm run build
# Built files go to jarvis/frontend/dist/
# FastAPI will serve them automatically from http://localhost:8000
```

---

## Configuration

Edit `jarvis/config.json` to customize:

| Key | Default | Description |
|---|---|---|
| `ollama_model` | `llama3.2:3b` | Ollama model name |
| `ollama_base_url` | `http://localhost:11434` | Ollama API URL |
| `stats_interval_seconds` | `5` | System stats refresh interval |
| `battery_interval_seconds` | `10` | Battery/network poll interval |
| `cpu_alert_threshold` | `90.0` | CPU % to trigger alert |
| `history_context_window` | `20` | Number of messages in AI context |
| `backend_port` | `8000` | FastAPI server port |
| `data_dir` | `./data` | Path to data directory |

Environment variables override config.json (prefix: `JARVIS_`):
- `JARVIS_OLLAMA_MODEL`, `JARVIS_PORT`, `JARVIS_DATA_DIR`, etc.

---

## Running Tests

```bash
# From jarvis/ directory
pip install pytest pytest-asyncio
pytest backend/tests/ -v
```

---

## Features (by unit)

| Unit | Status | Features |
|---|---|---|
| 1 — UI Foundation | ✅ Complete | FastAPI backend, React UI shell, WebSocket, config |
| 2 — Voice Module | 🔄 Pending | Speech recognition, TTS, voice waveform |
| 3 — AI Core | 🔄 Pending | Ollama chat, intent routing, conversation history |
| 4 — System Control | 🔄 Pending | OS control, file management, system monitoring, alerts |
| 5 — Browser Module | 🔄 Pending | Web search via browser-use |
| 6 — Coding Assistant | 🔄 Pending | Code generation, debugging, refactoring |
| 7 — Calendar & Tasks | 🔄 Pending | Task management, reminders |
