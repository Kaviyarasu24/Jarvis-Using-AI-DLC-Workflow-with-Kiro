/**
 * JarvisRing — Arc reactor / HUD ring animation.
 * Uses stroke-dasharray so arcs never overflow the SVG bounds.
 */

interface JarvisRingProps {
  active?: boolean
  size?: number
}

export default function JarvisRing({ active = false, size = 220 }: JarvisRingProps) {
  const cx = size / 2
  const cy = size / 2

  // Circumference helper
  const circ = (r: number) => 2 * Math.PI * r

  // Dash: show `fraction` of the circle, hide the rest
  const dash = (r: number, fraction: number) => {
    const c = circ(r)
    return `${c * fraction} ${c * (1 - fraction)}`
  }

  // Tick marks as a series of short dashes evenly spaced
  const tickDash = (r: number, count: number, tickLen: number) => {
    const c = circ(r)
    const segment = c / count
    const tick = (tickLen / (2 * Math.PI * r)) * c
    return `${tick} ${segment - tick}`
  }

  const r1 = size * 0.455  // outer
  const r2 = size * 0.375
  const r3 = size * 0.295
  const r4 = size * 0.215
  const r5 = size * 0.135  // core

  return (
    <div
      className="relative flex items-center justify-center select-none pointer-events-none"
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{ overflow: 'visible' }}
      >
        <defs>
          <filter id="glow-cyan" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="glow-gold" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <radialGradient id="core-grad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* ── Ring 1: Outer track ──────────────────────────────────── */}
        <circle cx={cx} cy={cy} r={r1}
          fill="none" stroke="#1e3a4a" strokeWidth={size * 0.024} />

        {/* Ring 1: Cyan arc — rotates CW 12s */}
        <circle cx={cx} cy={cy} r={r1}
          fill="none"
          stroke="#22d3ee"
          strokeWidth={size * 0.018}
          strokeDasharray={dash(r1, 0.78)}
          strokeDashoffset={circ(r1) * 0.25}
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          opacity="0.9"
          style={{
            transformOrigin: `${cx}px ${cy}px`,
            animation: 'ring-cw 12s linear infinite',
          }}
        />

        {/* Ring 1: Gold accent — rotates CW 12s (same group) */}
        <circle cx={cx} cy={cy} r={r1}
          fill="none"
          stroke="#f59e0b"
          strokeWidth={size * 0.018}
          strokeDasharray={dash(r1, 0.08)}
          strokeDashoffset={circ(r1) * 0.0}
          strokeLinecap="round"
          filter="url(#glow-gold)"
          opacity="0.9"
          style={{
            transformOrigin: `${cx}px ${cy}px`,
            animation: 'ring-cw 12s linear infinite',
          }}
        />

        {/* Ring 1: Tick marks (static) */}
        <circle cx={cx} cy={cy} r={r1 + size * 0.006}
          fill="none"
          stroke="#22d3ee"
          strokeWidth="0.8"
          strokeDasharray={tickDash(r1 + size * 0.006, 72, size * 0.022)}
          opacity="0.45"
        />
        <circle cx={cx} cy={cy} r={r1 + size * 0.006}
          fill="none"
          stroke="#22d3ee"
          strokeWidth="1.4"
          strokeDasharray={tickDash(r1 + size * 0.006, 12, size * 0.038)}
          opacity="0.65"
        />

        {/* ── Ring 2: Counter-rotating CCW 8s ─────────────────────── */}
        <circle cx={cx} cy={cy} r={r2}
          fill="none" stroke="#0f2a38" strokeWidth={size * 0.02} />

        <circle cx={cx} cy={cy} r={r2}
          fill="none"
          stroke="#38bdf8"
          strokeWidth={size * 0.013}
          strokeDasharray={dash(r2, 0.65)}
          strokeDashoffset={circ(r2) * 0.1}
          strokeLinecap="round"
          filter="url(#glow-cyan)"
          opacity="0.75"
          style={{
            transformOrigin: `${cx}px ${cy}px`,
            animation: 'ring-ccw 8s linear infinite',
          }}
        />

        <circle cx={cx} cy={cy} r={r2}
          fill="none"
          stroke="#f59e0b"
          strokeWidth={size * 0.013}
          strokeDasharray={dash(r2, 0.06)}
          strokeDashoffset={circ(r2) * 0.75}
          strokeLinecap="round"
          opacity="0.85"
          style={{
            transformOrigin: `${cx}px ${cy}px`,
            animation: 'ring-ccw 8s linear infinite',
          }}
        />

        <circle cx={cx} cy={cy} r={r2 + size * 0.004}
          fill="none"
          stroke="#38bdf8"
          strokeWidth="0.6"
          strokeDasharray={tickDash(r2 + size * 0.004, 48, size * 0.018)}
          opacity="0.35"
        />

        {/* ── Ring 3: CW 5s ───────────────────────────────────────── */}
        <circle cx={cx} cy={cy} r={r3}
          fill="none" stroke="#0a1f2e" strokeWidth={size * 0.016} />

        <circle cx={cx} cy={cy} r={r3}
          fill="none"
          stroke="#7dd3fc"
          strokeWidth={size * 0.01}
          strokeDasharray={dash(r3, 0.72)}
          strokeLinecap="round"
          opacity="0.65"
          style={{
            transformOrigin: `${cx}px ${cy}px`,
            animation: 'ring-cw 5s linear infinite',
          }}
        />

        <circle cx={cx} cy={cy} r={r3 + size * 0.003}
          fill="none"
          stroke="#7dd3fc"
          strokeWidth="0.5"
          strokeDasharray={tickDash(r3 + size * 0.003, 36, size * 0.016)}
          opacity="0.3"
        />

        {/* ── Ring 4: CCW 15s ─────────────────────────────────────── */}
        <circle cx={cx} cy={cy} r={r4}
          fill="none" stroke="#071520" strokeWidth={size * 0.012} />

        <circle cx={cx} cy={cy} r={r4}
          fill="none"
          stroke="#0ea5e9"
          strokeWidth={size * 0.008}
          strokeDasharray={dash(r4, 0.82)}
          strokeLinecap="round"
          opacity="0.55"
          style={{
            transformOrigin: `${cx}px ${cy}px`,
            animation: 'ring-ccw 15s linear infinite',
          }}
        />

        {/* ── Core glow + ring ────────────────────────────────────── */}
        <circle cx={cx} cy={cy} r={r5 + size * 0.025}
          fill="url(#core-grad)" />

        <circle cx={cx} cy={cy} r={r5}
          fill="none"
          stroke="#22d3ee"
          strokeWidth={size * 0.008}
          opacity={active ? 1 : 0.5}
          filter="url(#glow-cyan)"
          style={active ? { animation: 'pulse-ring 1.5s ease-in-out infinite' } : undefined}
        />

        {/* ── Active processing dots ───────────────────────────────── */}
        {active && [0, 120, 240].map((deg, i) => {
          const rad = (deg * Math.PI) / 180
          return (
            <circle
              key={i}
              cx={cx + r5 * 0.55 * Math.cos(rad)}
              cy={cy + r5 * 0.55 * Math.sin(rad)}
              r={size * 0.012}
              fill="#22d3ee"
              filter="url(#glow-cyan)"
              opacity="0.8"
              style={{ animation: `dot-pulse 1.5s ease-in-out ${i * 0.5}s infinite` }}
            />
          )
        })}
      </svg>

      {/* ── Center label ─────────────────────────────────────────────── */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="font-mono font-bold tracking-[0.2em] text-cyan-300"
          style={{
            fontSize: size * 0.09,
            textShadow: '0 0 12px #22d3ee, 0 0 24px #0ea5e9',
          }}
        >
          J.A.R.V.I.S
        </span>
        {active && (
          <span
            className="font-mono text-cyan-400 mt-1 animate-pulse"
            style={{ fontSize: size * 0.055, textShadow: '0 0 8px #22d3ee' }}
          >
            PROCESSING
          </span>
        )}
      </div>
    </div>
  )
}
