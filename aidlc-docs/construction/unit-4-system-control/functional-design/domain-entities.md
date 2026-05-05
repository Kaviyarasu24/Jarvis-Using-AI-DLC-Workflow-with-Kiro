# Unit 4: System Control & Monitoring — Domain Entities

## ActionResult
Result of a system control operation.

```
ActionResult
├── success: bool
├── output: str | None          — command output or file listing
├── requires_confirmation: bool — True if destructive and not yet confirmed
├── action_id: str | None       — UUID for pending confirmation
└── error: str | None
```

## SystemStats
Live system monitoring snapshot.

```
SystemStats
├── cpu_percent: float
├── ram_percent: float
├── ram_used_gb: float
├── ram_total_gb: float
├── disk_percent: float
├── disk_used_gb: float
├── disk_total_gb: float
├── battery_level: float | None
├── battery_charging: bool | None
├── network_connected: bool
├── processes: list[ProcessInfo]
└── timestamp: str              — ISO 8601
```

## ProcessInfo
A running process entry.

```
ProcessInfo
├── pid: int
├── name: str
└── cpu_percent: float
```

## Alert
A triggered monitoring alert.

```
Alert
├── id: str                     — UUID
├── type: str                   — "battery_connected" | "battery_disconnected" | "battery_high" | "battery_low" | "wifi_connected" | "wifi_disconnected" | "cpu_high"
├── message: str
├── severity: str               — "info" | "warning" | "critical"
└── timestamp: str
```

## PendingAction
A destructive action awaiting user confirmation.

```
PendingAction
├── action_id: str
├── action_type: str            — "delete_file" | "run_command"
├── params: dict
└── created_at: str
```
