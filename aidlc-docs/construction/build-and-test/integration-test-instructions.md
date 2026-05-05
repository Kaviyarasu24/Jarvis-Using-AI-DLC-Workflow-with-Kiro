# Integration Test Instructions — JARVIS

## Purpose
Test interactions between JARVIS modules to ensure the full pipeline works end-to-end.

## Prerequisites
- Backend running: `python -m backend.main` (from `jarvis/`)
- Ollama running: `ollama serve`
- Frontend running: `npm run dev` (from `jarvis/frontend/`)

---

## Scenario 1: WebSocket Chat Pipeline (Units 1 + 3)

**Tests**: UI Foundation → AI Core → Response

**Setup**: Backend + Ollama running

**Test Steps**:
1. Open `http://localhost:5173`
2. Type "Hello JARVIS" in the chat input
3. Press Enter

**Expected Result**:
- Message appears in chat as user bubble
- Typing indicator (dots) appears
- AI response appears within 10 seconds
- Response is coherent and in-character as JARVIS

---

## Scenario 2: Voice Pipeline (Units 1 + 2 + 3)

**Tests**: VoiceModule → IntentRouter → AICore → TTS

**Setup**: Microphone available, backend + Ollama running

**Test Steps**:
1. Click the microphone button in the chat input area
2. Speak: "What is the capital of France?"
3. Wait for response

**Expected Result**:
- Waveform animation appears while listening
- Transcribed text appears in chat
- AI response appears in chat
- Response is spoken aloud via TTS
- Speaking indicator shows during TTS

---

## Scenario 3: System Control (Units 1 + 3 + 4)

**Tests**: IntentRouter → SystemController → Confirmation flow

**Test Steps**:
1. Type: "list files in C:/"
2. Verify directory listing appears in chat
3. Type: "delete C:/nonexistent_test_file.txt"
4. Verify confirmation dialog appears
5. Click "Cancel"
6. Verify action is cancelled

**Expected Result**:
- Directory listing returned for non-destructive op
- Confirmation dialog shown for delete
- Cancel dismisses without deleting

---

## Scenario 4: System Monitoring (Units 1 + 4)

**Tests**: SystemMonitor → WebSocket → StatsSidebar

**Setup**: Backend running

**Test Steps**:
1. Open `http://localhost:5173`
2. Observe the right sidebar

**Expected Result**:
- CPU, RAM, disk percentages displayed with progress bars
- Values update every 5 seconds
- Battery level shown (if laptop)
- Network status shown

---

## Scenario 5: Calendar via Chat (Units 1 + 3 + 7)

**Tests**: IntentRouter → CalendarManager → REST

**Test Steps**:
1. Type: "add task Buy groceries for tomorrow"
2. Verify task added confirmation in chat
3. Type: "show today's tasks"
4. Click the calendar icon in the header
5. Verify CalendarPanel opens with task list

**Expected Result**:
- Task added confirmation message
- Today's tasks listed in chat
- CalendarPanel shows tasks with correct dates
- Reminders strip shows upcoming tasks

---

## Scenario 6: Coding Assistance (Units 1 + 3 + 6)

**Tests**: IntentRouter → CodingAssistant → Syntax highlighting

**Test Steps**:
1. Type: "write a Python function to calculate fibonacci numbers"
2. Wait for response

**Expected Result**:
- Response contains a code block with syntax highlighting
- Language label shows "python"
- Copy button visible on code block
- Code is syntactically correct Python

---

## Scenario 7: Alert Notifications (Unit 4)

**Tests**: SystemMonitor → WebSocket → NotificationBar

**Test Steps** (simulate by temporarily lowering CPU threshold):
1. Edit `config.json`: set `cpu_alert_threshold` to `1.0`
2. Restart backend
3. Open frontend

**Expected Result**:
- CPU high alert notification appears in top bar within 10 seconds
- Alert is dismissible (click X)
- Restore `cpu_alert_threshold` to `90.0` after test

---

## Cleanup

No persistent test data to clean up. Tasks added during testing can be removed via:
- Chat: "remove task Buy groceries"
- CalendarPanel: click trash icon on task
- Direct: delete `jarvis/data/tasks.json` and restart backend
