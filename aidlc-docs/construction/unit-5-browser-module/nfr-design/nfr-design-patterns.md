# Unit 5: Browser Module — NFR Design Patterns

## 1. Graceful Degradation
```python
async def search(self, query: str) -> BrowserResult:
    try:
        result = await asyncio.wait_for(
            self._run_browser_search(query),
            timeout=60.0
        )
        return result
    except asyncio.TimeoutError:
        return BrowserResult(success=False, query=query,
                             summary="", sources=[],
                             error="Search timed out. Please try again.")
    except Exception as e:
        logger.error(f"Browser search failed: {e}")
        return BrowserResult(success=False, query=query,
                             summary="", sources=[],
                             error="Web search failed. Please check your connection.")
```

## 2. Executor for Blocking browser-use
```python
async def _run_browser_search(self, query: str) -> BrowserResult:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self._search_sync, query)
```
