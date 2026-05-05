# Unit 4: System Control & Monitoring — Business Rules

## System Control Rules

| ID | Rule |
|---|---|
| BR-U4-001 | File deletion and shell command execution SHALL require explicit user confirmation before executing |
| BR-U4-002 | Confirmation SHALL be implemented via a `confirmation_required` WebSocket message to the frontend, followed by a `confirm_action` response |
| BR-U4-003 | Pending confirmations SHALL be stored in memory with a UUID action_id |
| BR-U4-004 | Pending confirmations SHALL expire after 60 seconds if not confirmed |
| BR-U4-005 | Non-destructive operations (open URL, launch app, list/read/copy/move files) SHALL execute immediately without confirmation |
| BR-U4-006 | Shell commands SHALL be executed with a 30-second timeout |
| BR-U4-007 | Shell command output SHALL be captured and returned as chat response text |
| BR-U4-008 | App launching SHALL use the OS default mechanism (Windows: `start` command) |

## System Monitoring Rules

| ID | Rule |
|---|---|
| BR-U4-010 | System stats SHALL be polled every `stats_interval_seconds` (default 5s) |
| BR-U4-011 | Battery and network SHALL be polled every `battery_interval_seconds` (default 10s) |
| BR-U4-012 | Stats SHALL be broadcast to all connected WebSocket clients as `stats_update` messages |
| BR-U4-013 | Alert conditions SHALL be evaluated on every battery/network poll |
| BR-U4-014 | Alerts SHALL only fire on state TRANSITIONS — not repeatedly while condition persists |

## Alert Rules

| ID | Rule |
|---|---|
| BR-U4-020 | Battery alert: charger connected — fires when `charging` transitions False → True |
| BR-U4-021 | Battery alert: charger disconnected — fires when `charging` transitions True → False |
| BR-U4-022 | Battery alert: high — fires when `level > 90` AND `charging=True` (once per charging session) |
| BR-U4-023 | Battery alert: low — fires when `level < 30` AND `charging=False` (once per discharge cycle) |
| BR-U4-024 | Network alert: Wi-Fi connected — fires when `connected` transitions False → True |
| BR-U4-025 | Network alert: Wi-Fi disconnected — fires when `connected` transitions True → False |
| BR-U4-026 | CPU alert: fires when `cpu_percent > cpu_alert_threshold` (default 90%) — max once per minute |
