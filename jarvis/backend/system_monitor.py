"""
SystemMonitor — background asyncio task that polls system stats via psutil
and broadcasts updates + alerts over WebSocket.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import psutil

from .config_manager import ConfigManager
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# Try importing pycaw for Windows volume monitoring
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    _PYCAW_AVAILABLE = True
except Exception:
    _PYCAW_AVAILABLE = False
    logger.warning("pycaw not available — volume/mute monitoring disabled.")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BatterySnapshot:
    level: float
    charging: bool


@dataclass
class Alert:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    message: str = ""
    severity: str = "info"
    timestamp: str = field(default_factory=_now_iso)


class SystemMonitor:
    """Polls system metrics and pushes stats + alerts to the frontend via WebSocket."""

    def __init__(self, config: ConfigManager, ws_manager: WebSocketManager) -> None:
        self._config = config
        self._ws = ws_manager
        self._task: Optional[asyncio.Task] = None

        # Previous state for transition detection
        self._prev_battery: Optional[BatterySnapshot] = None
        self._prev_network: Optional[bool] = None
        self._battery_high_alerted = False
        self._battery_low_alerted = False
        self._cpu_alert_last: Optional[float] = None

        # Volume monitoring state
        self._prev_volume: Optional[int] = None   # 0–100
        self._prev_muted: Optional[bool] = None
        self._volume_change_timer: Optional[float] = None  # debounce

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the background monitoring loop."""
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run_with_restart())
        logger.info("SystemMonitor started.")

    async def stop(self) -> None:
        """Stop the monitoring loop."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SystemMonitor stopped.")

    # ------------------------------------------------------------------
    # Stats collection
    # ------------------------------------------------------------------

    async def get_stats(self) -> dict:
        """Return a current stats snapshot as a dict."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._collect_stats_sync)

    def _collect_stats_sync(self) -> dict:
        """Blocking: collect all system stats via psutil."""
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Battery (may be None on desktops)
        battery_level = None
        battery_charging = None
        try:
            bat = psutil.sensors_battery()
            if bat:
                battery_level = round(bat.percent, 1)
                battery_charging = bat.power_plugged
        except Exception:
            pass

        # Network connectivity (simple check)
        network_connected = self._check_network()

        # Top processes by CPU
        processes = []
        try:
            for proc in sorted(
                psutil.process_iter(["pid", "name", "cpu_percent"]),
                key=lambda p: p.info.get("cpu_percent") or 0,
                reverse=True,
            )[:5]:
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cpu_percent": round(proc.info.get("cpu_percent") or 0, 1),
                })
        except Exception:
            pass

        return {
            "cpu_percent": round(cpu, 1),
            "ram_percent": round(ram.percent, 1),
            "ram_used_gb": round(ram.used / 1e9, 2),
            "ram_total_gb": round(ram.total / 1e9, 2),
            "disk_percent": round(disk.percent, 1),
            "disk_used_gb": round(disk.used / 1e9, 1),
            "disk_total_gb": round(disk.total / 1e9, 1),
            "battery_level": battery_level,
            "battery_charging": battery_charging,
            "network_connected": network_connected,
            "processes": processes,
            "timestamp": _now_iso(),
        }

    def _check_network(self) -> bool:
        """Check network connectivity via psutil net_if_stats."""
        try:
            stats = psutil.net_if_stats()
            return any(iface.isup for iface in stats.values())
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Alert detection
    # ------------------------------------------------------------------

    def _check_battery_alerts(self, stats: dict) -> list[Alert]:
        alerts = []
        level = stats.get("battery_level")
        charging = stats.get("battery_charging")

        if level is None or charging is None:
            return []

        current = BatterySnapshot(level=level, charging=charging)
        prev = self._prev_battery

        if prev is not None:
            # Charger connected/disconnected
            if current.charging != prev.charging:
                if current.charging:
                    alerts.append(Alert(
                        type="battery_connected",
                        message="Charger connected",
                        severity="info",
                    ))
                    self._battery_high_alerted = False  # reset for new charging session
                else:
                    alerts.append(Alert(
                        type="battery_disconnected",
                        message="Charger disconnected",
                        severity="warning",
                    ))
                    self._battery_low_alerted = False  # reset for new discharge cycle

            # High battery while charging (once per session)
            if current.level > 90 and current.charging and not self._battery_high_alerted:
                alerts.append(Alert(
                    type="battery_high",
                    message=f"Battery at {current.level:.0f}% while charging — consider unplugging",
                    severity="info",
                ))
                self._battery_high_alerted = True

            # Low battery while discharging (once per cycle)
            if current.level < 30 and not current.charging and not self._battery_low_alerted:
                alerts.append(Alert(
                    type="battery_low",
                    message=f"Battery at {current.level:.0f}% — please charge soon",
                    severity="warning",
                ))
                self._battery_low_alerted = True

        self._prev_battery = current
        return alerts

    def _check_network_alerts(self, stats: dict) -> list[Alert]:
        alerts = []
        connected = stats.get("network_connected", False)
        prev = self._prev_network

        if prev is not None and connected != prev:
            if connected:
                alerts.append(Alert(
                    type="wifi_connected",
                    message="Wi-Fi connected",
                    severity="info",
                ))
            else:
                alerts.append(Alert(
                    type="wifi_disconnected",
                    message="Wi-Fi disconnected",
                    severity="warning",
                ))

        self._prev_network = connected
        return alerts

    def _check_cpu_alert(self, stats: dict) -> list[Alert]:
        cpu = stats.get("cpu_percent", 0)
        threshold = self._config.cpu_alert_threshold
        now = datetime.now(timezone.utc).timestamp()

        if cpu > threshold:
            # Rate-limit: max once per 60 seconds
            if self._cpu_alert_last is None or (now - self._cpu_alert_last) > 60:
                self._cpu_alert_last = now
                return [Alert(
                    type="cpu_high",
                    message=f"High CPU usage: {cpu:.0f}%",
                    severity="critical",
                )]
        return []

    def _get_volume_state(self) -> tuple[Optional[int], Optional[bool]]:
        """Get current system volume (0-100) and mute state. Returns (None, None) if unavailable."""
        if not _PYCAW_AVAILABLE:
            return None, None
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            level = round(volume.GetMasterVolumeLevelScalar() * 100)
            muted = bool(volume.GetMute())
            return level, muted
        except Exception as e:
            logger.debug(f"Volume check failed: {e}")
            return None, None

    def _check_volume_alerts(self, volume: Optional[int], muted: Optional[bool]) -> list[Alert]:
        """Detect mute/unmute and significant volume changes."""
        alerts = []
        if volume is None or muted is None:
            return []

        now = datetime.now(timezone.utc).timestamp()

        # Mute/unmute transitions
        if self._prev_muted is not None and muted != self._prev_muted:
            if muted:
                alerts.append(Alert(
                    type="volume_muted",
                    message="🔇 Sound muted",
                    severity="info",
                ))
            else:
                alerts.append(Alert(
                    type="volume_unmuted",
                    message=f"🔊 Sound unmuted — {volume}%",
                    severity="info",
                ))

        # Volume change (debounced — only alert if changed by ≥5% and settled)
        if self._prev_volume is not None and not muted and abs(volume - self._prev_volume) >= 5:
            # Use a simple debounce: only fire if we haven't fired in last 2s
            if self._volume_change_timer is None or (now - self._volume_change_timer) > 2.0:
                self._volume_change_timer = now
                icon = "🔊" if volume > 50 else "🔉" if volume > 0 else "🔈"
                alerts.append(Alert(
                    type="volume_changed",
                    message=f"{icon} Volume: {volume}%",
                    severity="info",
                ))

        self._prev_volume = volume
        self._prev_muted = muted
        return alerts

    # ------------------------------------------------------------------
    # Internal: monitoring loop
    # ------------------------------------------------------------------

    async def _run_with_restart(self) -> None:
        """Auto-restart the monitoring loop on unexpected errors."""
        while True:
            try:
                await self._monitor_loop()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor loop crashed: {e}. Restarting in 5s.")
                await asyncio.sleep(5)

    async def _monitor_loop(self) -> None:
        """Main monitoring loop — polls stats and emits WebSocket events."""
        battery_elapsed = 0.0

        while True:
            await asyncio.sleep(self._config.stats_interval_seconds)
            battery_elapsed += self._config.stats_interval_seconds

            # Collect stats
            stats = await self.get_stats()
            await self._ws.broadcast("stats_update", stats)

            # Battery + network alerts (less frequent)
            if battery_elapsed >= self._config.battery_interval_seconds:
                battery_elapsed = 0.0
                alerts = (
                    self._check_battery_alerts(stats)
                    + self._check_network_alerts(stats)
                    + self._check_cpu_alert(stats)
                )
                for alert in alerts:
                    await self._ws.broadcast("alert", {
                        "id": alert.id,
                        "type": alert.type,
                        "message": alert.message,
                        "severity": alert.severity,
                        "timestamp": alert.timestamp,
                    })
                    logger.info(f"Alert fired: {alert.type} — {alert.message}")

            # Volume monitoring (every stats interval — fast check)
            loop = asyncio.get_event_loop()
            vol, muted = await loop.run_in_executor(None, self._get_volume_state)
            vol_alerts = self._check_volume_alerts(vol, muted)
            for alert in vol_alerts:
                await self._ws.broadcast("alert", {
                    "id": alert.id,
                    "type": alert.type,
                    "message": alert.message,
                    "severity": alert.severity,
                    "timestamp": alert.timestamp,
                })
                logger.info(f"Alert fired: {alert.type} — {alert.message}")
