# Unit 4: System Control & Monitoring — Logical Components

| Component | Purpose |
|---|---|
| `SystemController` | Parses system commands, executes OS operations, manages confirmation flow |
| `SystemMonitor` | Background asyncio task, psutil polling, alert detection, WebSocket broadcast |
| `psutil` | CPU/RAM/disk/battery/network data collection |
| `subprocess` | Shell command execution with timeout |
| `webbrowser` | URL opening |
| `shutil` / `pathlib` | File operations |
| `WebSocketManager` (Unit 1) | Broadcasts stats_update and alert messages |
| `IntentRouter` (Unit 3) | Routes "system" intent to SystemController |
| `StatsSidebar` (React) | Displays live stats from stats_update messages |
| `NotificationBar` (React) | Displays alert notifications |
