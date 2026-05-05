# Unit 4: System Control & Monitoring — Tech Stack Decisions

| Component | Choice | Rationale |
|---|---|---|
| System monitoring | `psutil` 5.9+ | User-specified; cross-platform; CPU/RAM/disk/battery/network |
| Shell execution | `subprocess` (stdlib) | Standard; captures stdout/stderr; timeout support |
| App launching | `subprocess` + `os.startfile` (Windows) | Windows-native app launch |
| URL opening | `webbrowser` (stdlib) | Cross-platform URL opening |
| File operations | `shutil` + `pathlib` (stdlib) | Standard file copy/move/delete |
| Async bridge | `asyncio.run_in_executor` | psutil and subprocess are blocking — run off event loop |
| Alert IDs | `uuid.uuid4()` | Unique action IDs for confirmation flow |
