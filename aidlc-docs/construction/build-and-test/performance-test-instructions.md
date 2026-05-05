# Performance Test Instructions — JARVIS

## Performance Requirements (from NFRs)

| Metric | Target | Source |
|---|---|---|
| AI response latency | < 10 seconds | NFR-001 |
| Voice recognition processing | < 2 seconds | NFR-002 |
| System stats refresh | Every 5 seconds | NFR-003 |
| Battery/network poll | Every 10 seconds | NFR-004 |
| Application startup | < 5 seconds | NFR-023 |

## Note on Performance Context

JARVIS is a **single-user local application** running on CPU inference (llama3.2:3b via Ollama). Performance targets are calibrated for this context — not for concurrent users or cloud deployment.

From the Ollama logs provided: `available="4.6 GiB"` RAM available for inference. llama3.2:3b requires ~2GB RAM. Response times will vary based on query complexity.

---

## Test 1: AI Response Latency

**Method**: Manual timing

**Steps**:
1. Start backend + Ollama
2. Open frontend
3. Send a simple query: "What is 2 + 2?"
4. Measure time from send to response display

**Expected**: < 10 seconds on CPU inference with 4.6 GiB available RAM

**Typical range**: 3–8 seconds for llama3.2:3b on CPU

---

## Test 2: Application Startup Time

**Steps**:
1. Stop backend if running
2. Time the startup: `python -m backend.main`
3. Measure from command execution to "JARVIS ready." log line

**Expected**: < 5 seconds

---

## Test 3: System Stats Refresh Rate

**Steps**:
1. Open frontend with backend running
2. Watch the StatsSidebar
3. Verify values update approximately every 5 seconds

**Expected**: Stats update every 5 ± 1 seconds

---

## Test 4: WebSocket Latency

**Steps**:
1. Open browser DevTools → Network → WS
2. Send a message
3. Observe WebSocket frame timing

**Expected**: WebSocket round-trip (excluding AI inference) < 100ms

---

## Performance Optimization Notes

If AI responses are consistently > 10 seconds:
1. Check available RAM: `psutil.virtual_memory().available`
2. Consider reducing `history_context_window` in `config.json` (fewer tokens = faster)
3. Consider a smaller model: `ollama pull llama3.2:1b`
4. Ensure no other heavy processes are running

If startup is slow:
1. Check if `speech_recognition` microphone check is blocking — it has a 0.1s ambient noise adjustment
2. Ensure `data/` directory exists (auto-created, but first run may be slightly slower)
