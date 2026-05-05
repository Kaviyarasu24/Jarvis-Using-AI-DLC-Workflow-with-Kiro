# Unit 2: Voice Module — Frontend Components

## VoiceIndicator (Full Implementation)

Replaces the Unit 1 placeholder with a fully functional voice toggle button and animated waveform.

### Props
```typescript
// No props — reads from WebSocketContext
```

### State
```typescript
const [voiceEnabled, setVoiceEnabled] = useState(false)
const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>('idle')
const [micAvailable, setMicAvailable] = useState(true)
```

### Behavior

**On `voice_status` WebSocket message:**
- `"toggled"` + `enabled=true` → set `voiceEnabled=true`
- `"toggled"` + `enabled=false` → set `voiceEnabled=false`
- `"listening_start"` → set `voiceStatus='listening_start'` (show waveform animation)
- `"listening_end"` → set `voiceStatus='listening_end'`
- `"speaking_start"` → set `voiceStatus='speaking_start'` (show speaking indicator)
- `"speaking_end"` → set `voiceStatus='speaking_end'`, reset to idle
- `"error"` with `error="Microphone not available"` → set `micAvailable=false`

**On button click:**
- Send `voice_toggle` WebSocket message with `enabled: !voiceEnabled`

### Visual States

| State | Visual |
|---|---|
| Mic unavailable | Disabled `MicOff` icon, greyed out |
| Voice off | `Mic` icon, muted color, clickable |
| Voice on (idle) | `Mic` icon, accent color, pulsing ring |
| Listening | Animated waveform bars (3 bars bouncing) |
| Speaking | Speaker wave icon, accent color |

### Component Structure
```tsx
<div data-testid="voice-indicator">
  <button
    data-testid="voice-toggle-btn"
    onClick={handleToggle}
    disabled={!micAvailable}
    className={...}
    aria-label={voiceEnabled ? "Disable voice" : "Enable voice"}
    title={...}
  >
    {/* Icon based on state */}
  </button>
  
  {/* Waveform animation when listening */}
  {voiceStatus === 'listening_start' && (
    <div data-testid="voice-waveform" className="waveform-bars">
      <span /><span /><span />
    </div>
  )}
</div>
```
