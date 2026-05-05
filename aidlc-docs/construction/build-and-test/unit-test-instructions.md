# Unit Test Execution — JARVIS

## Prerequisites

```bash
# From jarvis/ directory
pip install pytest pytest-asyncio
```

Add `pytest.ini` for asyncio mode:

```ini
[pytest]
asyncio_mode = auto
```

---

## Run All Unit Tests

```bash
# From jarvis/ directory
pytest backend/tests/ -v
```

**Expected output**: All tests pass, 0 failures.

---

## Test Suites by Module

### Unit 1: UI Foundation
```bash
pytest backend/tests/test_config_manager.py -v
pytest backend/tests/test_websocket_manager.py -v
```
- `test_config_manager.py` — 10 tests: defaults, file loading, env overrides, type coercion
- `test_websocket_manager.py` — 8 tests: connect, disconnect, send, receive, malformed input

### Unit 2: Voice Module
```bash
pytest backend/tests/test_voice_module.py -v
```
- 14 tests: init, toggle, TTS events, STT transcription/timeout/errors

### Unit 3: AI Core
```bash
pytest backend/tests/test_ai_core.py -v
pytest backend/tests/test_intent_router.py -v
```
- `test_ai_core.py` — 13 tests: history CRUD, chat, Ollama errors, intent classification
- `test_intent_router.py` — 4 tests: routing, fallback, error handling, registration

### Unit 4: System Control & Monitoring
```bash
pytest backend/tests/test_system_controller.py -v
```
- 14 tests: file operations, destructive confirmation, alert transition detection

### Unit 5: Browser Module
```bash
pytest backend/tests/test_browser_module.py -v
```
- 9 tests: query extraction, unavailable browser, result structure

### Unit 6: Coding Assistant
```bash
pytest backend/tests/test_coding_assistant.py -v
```
- 16 tests: task type detection, code block extraction, handle pipeline

### Unit 7: Calendar & Tasks
```bash
pytest backend/tests/test_calendar_manager.py -v
```
- 18 tests: CRUD, persistence, NL parsing, date extraction

---

## Total Test Count

| Module | Tests |
|---|---|
| ConfigManager | 10 |
| WebSocketManager | 8 |
| VoiceModule | 14 |
| AICore | 13 |
| IntentRouter | 4 |
| SystemController + Monitor | 14 |
| BrowserModule | 9 |
| CodingAssistant | 16 |
| CalendarManager | 18 |
| **Total** | **106** |

---

## Expected Results

```
========================= 106 passed in X.XXs =========================
```

## Coverage Report

```bash
pip install pytest-cov
pytest backend/tests/ --cov=backend --cov-report=term-missing -v
```

## Fix Failing Tests

1. Read the test output — pytest shows exact assertion failures
2. Check if the module under test has the expected method/behavior
3. Most tests use mocks — ensure mock return values match expected types
4. For async tests, ensure `pytest-asyncio` is installed and `asyncio_mode = auto` is set
