# Unit 3: AI Core — NFR Design Patterns

## 1. Graceful Degradation — Ollama Unavailable
```python
async def _ollama_request(self, messages, system=None):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(...)
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise OllamaUnavailableError("Cannot connect to Ollama")
    except httpx.TimeoutException:
        raise OllamaTimeoutError("Ollama request timed out")
```

## 2. Atomic History Write — Prevent Corruption
```python
def save_history(self):
    tmp = self._history_path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump({"messages": self._messages}, f, indent=2)
    tmp.replace(self._history_path)  # atomic on same filesystem
```

## 3. Dependency Injection for Testability
```python
class AICore:
    def __init__(self, config, http_client=None):
        self._http_client = http_client  # inject mock in tests
```

## 4. Context Window Truncation
```python
def get_context_window(self, n: int) -> list[dict]:
    # Always include system message + last N user/assistant messages
    return [{"role": m["role"], "content": m["content"]}
            for m in self._messages[-n:]]
```
