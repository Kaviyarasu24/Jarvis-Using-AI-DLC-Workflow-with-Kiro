# JARVIS Application Design Plan

## Plan Overview
Design the component architecture, interfaces, service layer, and dependency map for JARVIS — a 7-module AI personal assistant with a FastAPI backend and React + TypeScript frontend.

---

## Execution Checklist

- [x] Step 1: Answer design clarification questions
- [x] Step 2: Generate `components.md` — component definitions and responsibilities
- [x] Step 3: Generate `component-methods.md` — method signatures and interfaces
- [x] Step 4: Generate `services.md` — service layer and orchestration patterns
- [x] Step 5: Generate `component-dependency.md` — dependency matrix and data flow
- [x] Step 6: Generate `application-design.md` — consolidated design document
- [x] Step 7: Validate design completeness and consistency

---

## Design Clarification Questions

Please answer the following questions by filling in the letter choice after each `[Answer]:` tag.

---

### Question 1
How should the FastAPI backend communicate with the React frontend for real-time updates (system stats, alerts, voice status)?

A) WebSockets — persistent connection for real-time push (recommended for live stats + alerts)
B) Server-Sent Events (SSE) — one-way server push stream
C) Polling — frontend polls REST endpoints every N seconds
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2
How should the intent routing work — how does JARVIS decide which module handles a user message?

A) Keyword/pattern matching — detect keywords like "search", "open", "code", "remind" to route to the right module
B) LLM-based intent classification — ask the Ollama model to classify the intent first, then route
C) Hybrid — keyword matching first, fall back to LLM classification for ambiguous inputs
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Question 3
Should the voice pipeline (STT + TTS) run in the backend (Python process) or be handled differently?

A) Fully in the backend — Python process handles microphone capture, STT, and TTS; frontend just shows status
B) STT in backend, TTS in backend — frontend sends a "start listening" signal via API
C) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 4
How should system monitoring stats be delivered to the React frontend?

A) Via the same WebSocket/SSE connection used for chat (multiplexed messages)
B) Separate dedicated REST endpoint polled by the frontend every 5 seconds
C) Separate WebSocket channel dedicated to monitoring data
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 5
For the React frontend component structure, which layout approach do you prefer?

A) Single-page layout — chat panel center, system stats sidebar right, notifications top bar
B) Tabbed layout — separate tabs for Chat, System Monitor, Calendar/Tasks
C) Split-panel layout — resizable panels for chat and tools
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 6
Should the Calendar/Task module be accessible through the chat interface only, or also have a dedicated UI panel?

A) Chat only — user manages tasks via natural language commands in the chat
B) Dedicated panel — a separate calendar/task view in the UI alongside chat
C) Both — chat commands + a dedicated panel
D) Other (please describe after [Answer]: tag below)

[Answer]: C
