# Unit 4: System Control & Monitoring — NFR Design Patterns

## 1. Executor Pattern for Blocking I/O
psutil and subprocess are blocking. All calls run in a thread pool executor:

```python
async def get_stats(self) -> SystemStats:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self._collect_stats_sync)
```

## 2. Transition-Based Alert Detection
Alerts fire only on state changes, not continuously:

```python
# Store previous state; compare on each poll
if current.charging != self._prev_charging:
    yield Alert("battery_connected" if current.charging else "battery_disconnected", ...)
self._prev_charging = current.charging
```

## 3. Confirmation Gate Pattern
Destructive operations are two-phase:
1. First call: store pending action, return `requires_confirmation=True`
2. Second call (after user confirms): execute with `confirmed=True`

```python
if not confirmed:
    action_id = str(uuid.uuid4())
    self._pending[action_id] = PendingAction(...)
    return ActionResult(requires_confirmation=True, action_id=action_id)
# Execute only when confirmed=True
```

## 4. Auto-Restart Monitoring Loop
```python
async def start(self):
    while True:
        try:
            await self._monitor_loop()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Monitor loop crashed: {e}. Restarting in 5s.")
            await asyncio.sleep(5)
```
