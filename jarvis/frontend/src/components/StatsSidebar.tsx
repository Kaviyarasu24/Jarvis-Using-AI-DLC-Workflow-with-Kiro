import { Cpu, MemoryStick, HardDrive, Battery, Wifi, WifiOff } from 'lucide-react'
import type { SystemStats } from '../types'

interface StatsSidebarProps {
  stats: SystemStats | null
}

function ProgressBar({ value, color = 'bg-jarvis-accent' }: { value: number; color?: string }) {
  return (
    <div className="w-full bg-jarvis-border rounded-full h-1.5 mt-1">
      <div
        className={`h-1.5 rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${Math.min(value, 100)}%` }}
      />
    </div>
  )
}

function StatRow({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: number
  color?: string
}) {
  return (
    <div className="mb-3">
      <div className="flex items-center justify-between text-xs text-jarvis-muted mb-0.5">
        <span className="flex items-center gap-1.5">
          {icon}
          {label}
        </span>
        <span className="text-jarvis-text font-medium">{value.toFixed(0)}%</span>
      </div>
      <ProgressBar value={value} color={color} />
    </div>
  )
}

function SkeletonRow() {
  return (
    <div className="mb-3 animate-pulse">
      <div className="flex justify-between mb-1">
        <div className="h-3 bg-jarvis-border rounded w-20" />
        <div className="h-3 bg-jarvis-border rounded w-8" />
      </div>
      <div className="h-1.5 bg-jarvis-border rounded-full" />
    </div>
  )
}

export default function StatsSidebar({ stats }: StatsSidebarProps) {
  const cpuColor = stats && stats.cpu_percent > 90 ? 'bg-jarvis-danger' :
    stats && stats.cpu_percent > 70 ? 'bg-jarvis-warning' : 'bg-jarvis-accent'

  const ramColor = stats && stats.ram_percent > 90 ? 'bg-jarvis-danger' :
    stats && stats.ram_percent > 70 ? 'bg-jarvis-warning' : 'bg-jarvis-info'

  return (
    <aside
      data-testid="stats-sidebar"
      className="w-64 flex-shrink-0 bg-jarvis-card border-l border-jarvis-border p-4 overflow-y-auto"
    >
      <h2 className="text-xs font-semibold text-jarvis-muted uppercase tracking-wider mb-4">
        System Monitor
      </h2>

      {!stats ? (
        <>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </>
      ) : (
        <>
          <StatRow
            icon={<Cpu size={12} />}
            label="CPU"
            value={stats.cpu_percent}
            color={cpuColor}
          />
          <StatRow
            icon={<MemoryStick size={12} />}
            label={`RAM (${stats.ram_used_gb.toFixed(1)}/${stats.ram_total_gb.toFixed(1)} GB)`}
            value={stats.ram_percent}
            color={ramColor}
          />
          <StatRow
            icon={<HardDrive size={12} />}
            label={`Disk (${stats.disk_used_gb.toFixed(0)}/${stats.disk_total_gb.toFixed(0)} GB)`}
            value={stats.disk_percent}
          />

          {/* Battery */}
          {stats.battery_level !== null && (
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs text-jarvis-muted mb-0.5">
                <span className="flex items-center gap-1.5">
                  <Battery size={12} />
                  Battery {stats.battery_charging ? '⚡' : ''}
                </span>
                <span className="text-jarvis-text font-medium">
                  {stats.battery_level.toFixed(0)}%
                </span>
              </div>
              <ProgressBar
                value={stats.battery_level}
                color={
                  stats.battery_level < 30 ? 'bg-jarvis-danger' :
                  stats.battery_level < 50 ? 'bg-jarvis-warning' : 'bg-jarvis-success'
                }
              />
            </div>
          )}

          {/* Network */}
          <div className="flex items-center gap-2 text-xs mt-4">
            {stats.network_connected ? (
              <>
                <Wifi size={12} className="text-jarvis-success" />
                <span className="text-jarvis-success">Connected</span>
              </>
            ) : (
              <>
                <WifiOff size={12} className="text-jarvis-danger" />
                <span className="text-jarvis-danger">Disconnected</span>
              </>
            )}
          </div>
        </>
      )}
    </aside>
  )
}
