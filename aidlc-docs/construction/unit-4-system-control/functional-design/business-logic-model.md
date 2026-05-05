# Unit 4: System Control & Monitoring — Business Logic Model

## 1. System Command Parsing

The IntentRouter routes "system" intent to SystemController. The controller parses the natural language command to determine the operation:

```
parse_command(message) -> (operation, params)

Patterns:
  "open https://..." | "open url ..."     -> open_url(url)
  "open <app>" | "launch <app>"           -> launch_app(app_name)
  "list files in <path>" | "ls <path>"    -> list_directory(path)
  "read file <path>"                      -> read_file(path)
  "copy <src> to <dst>"                   -> copy_file(src, dst)
  "move <src> to <dst>"                   -> move_file(src, dst)
  "delete <path>" | "remove <path>"       -> delete_file(path)  [requires confirmation]
  "run <command>" | "execute <command>"   -> run_command(cmd)   [requires confirmation]
```

## 2. Confirmation Flow

```
User: "delete C:/temp/old.txt"
      |
      v
SystemController.delete_file("C:/temp/old.txt", confirmed=False)
      |
      v
Returns ActionResult(requires_confirmation=True, action_id="uuid-123")
      |
      v
main.py sends: WSMessage(type="confirmation_required", payload={
  action_id: "uuid-123",
  action: "delete_file",
  details: "Delete file: C:/temp/old.txt"
})
      |
      v
Frontend shows confirmation dialog
      |
      v
User clicks "Confirm"
      |
      v
Frontend sends: WSMessage(type="confirm_action", payload={ action_id: "uuid-123" })
      |
      v
main.py looks up pending action by action_id
      |
      v
SystemController.delete_file("C:/temp/old.txt", confirmed=True)
      |
      v
Returns ActionResult(success=True, output="File deleted.")
```

## 3. Monitoring Loop

```
BACKGROUND TASK: _monitor_loop()

  stats_counter = 0
  battery_counter = 0
  prev_battery = None
  prev_network = None
  cpu_alert_last = None

  LOOP:
    SLEEP stats_interval_seconds
    
    # Always collect stats
    stats = collect_stats()
    broadcast stats_update(stats)
    
    # Battery + network check (less frequent)
    battery_counter += stats_interval_seconds
    IF battery_counter >= battery_interval_seconds:
      battery_counter = 0
      alerts = check_battery_alerts(stats.battery, prev_battery)
      alerts += check_network_alerts(stats.network_connected, prev_network)
      alerts += check_cpu_alert(stats.cpu_percent, cpu_alert_last)
      FOR alert IN alerts:
        broadcast alert(alert)
      prev_battery = stats.battery
      prev_network = stats.network_connected
```

## 4. Alert Transition Detection

```
check_battery_alerts(current, previous) -> list[Alert]:
  alerts = []
  IF previous is None: RETURN []  # first poll, no transition
  
  # Charger connected/disconnected
  IF current.charging != previous.charging:
    IF current.charging:
      alerts.append(Alert("battery_connected", "Charger connected", "info"))
    ELSE:
      alerts.append(Alert("battery_disconnected", "Charger disconnected", "warning"))
  
  # High battery while charging (once per session)
  IF current.level > 90 AND current.charging AND NOT (previous.level > 90 AND previous.charging):
    alerts.append(Alert("battery_high", "Battery above 90% — consider unplugging", "info"))
  
  # Low battery while discharging (once per cycle)
  IF current.level < 30 AND NOT current.charging AND NOT (previous.level < 30 AND NOT previous.charging):
    alerts.append(Alert("battery_low", "Battery below 30% — please charge", "warning"))
  
  RETURN alerts
```
