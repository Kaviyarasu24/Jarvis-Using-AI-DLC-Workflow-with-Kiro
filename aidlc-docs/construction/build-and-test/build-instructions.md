# Build Instructions — JARVIS

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| npm | 9+ | Frontend package manager |
| Ollama | 0.22+ | Local LLM server |
| llama3.2:3b model | — | `ollama pull llama3.2:3b` |
| Windows | 10/11 | Primary target OS |
| Microphone | — | Optional (for voice features) |

## Environment Variables (Optional Overrides)

All have defaults in `config.json`. Override via environment variables if needed:

```bash
set JARVIS_OLLAMA_MODEL=llama3.2:3b
set JARVIS_OLLAMA_BASE_URL=http://localhost:11434
set JARVIS_PORT=8000
set JARVIS_DATA_DIR=./data
```

---

## Backend Build

### 1. Install Python Dependencies

```bash
# From jarvis/ directory
pip install -r requirements.txt
```

**Expected output**: All packages installed successfully. Key packages:
- `fastapi==0.111.0`
- `uvicorn[standard]==0.29.0`
- `psutil==5.9.8`
- `SpeechRecognition==3.10.4`
- `pyttsx3==2.90`
- `httpx==0.27.0`

**Windows note for PyAudio**: If `pyaudio` fails to install, download the pre-built wheel:
```bash
# Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then install:
pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl
```

### 2. Verify Ollama is Running

```bash
ollama serve
# In a separate terminal, verify:
curl http://localhost:11434/api/tags
```

### 3. Start the Backend

```bash
# From jarvis/ directory
python -m backend.main
```

**Expected output**:
```
INFO: JARVIS starting up...
INFO: Data directory ready: .../jarvis/data
INFO: Config loaded from config.json
INFO: Loaded X messages from history.
INFO: Loaded X tasks.
INFO: Voice available: True/False
INFO: SystemMonitor started.
INFO: JARVIS ready.
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Build artifacts**: Running FastAPI server on `http://localhost:8000`

---

## Frontend Build

### 1. Install Node Dependencies

```bash
# From jarvis/frontend/ directory
npm install
```

**Expected output**: `added X packages` with no errors.

**Note**: `react-syntax-highlighter` must be installed:
```bash
npm install react-syntax-highlighter @types/react-syntax-highlighter
```

### 2. Development Build (with hot reload)

```bash
# From jarvis/frontend/ directory
npm run dev
```

**Expected output**:
```
VITE v5.x.x  ready in Xms
➜  Local:   http://localhost:5173/
```

### 3. Production Build

```bash
# From jarvis/frontend/ directory
npm run build
```

**Expected output**: `dist/` directory created in `jarvis/frontend/`

**Build artifacts**: `jarvis/frontend/dist/` — served automatically by FastAPI

---

## Full Stack Startup (Development)

Run these in separate terminals:

**Terminal 1 — Ollama:**
```bash
ollama serve
```

**Terminal 2 — Backend:**
```bash
cd jarvis
python -m backend.main
```

**Terminal 3 — Frontend:**
```bash
cd jarvis/frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'backend'`
Run from the `jarvis/` directory, not `jarvis/backend/`:
```bash
cd jarvis
python -m backend.main
```

### `pyttsx3` fails on Windows
```bash
pip install pywin32
```

### `speech_recognition` microphone error
Install PyAudio (see step 1 above). Voice features will be disabled gracefully if unavailable.

### `browser-use` import error
```bash
pip install browser-use langchain-ollama
```

### Frontend `react-syntax-highlighter` not found
```bash
cd jarvis/frontend
npm install react-syntax-highlighter @types/react-syntax-highlighter
```
