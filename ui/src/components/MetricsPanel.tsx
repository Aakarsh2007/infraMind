import React from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

function Bar({ value, warn, crit }: { value: number; warn: number; crit: number }) {
  const color = value > crit ? '#ef4444' : value > warn ? '#f59e0b' : '#22c55e'
  return (
    <div style={{ height: 4, background: '#1e2d4a', borderRadius: 2, marginTop: 3 }}>
      <div style={{ height: '100%', width: `${Math.min(100, value)}%`, background: color, borderRadius: 2, transition: 'width 0.4s ease' }} />
    </div>
  )
}

function Row({ label, value, unit, warn = 70, crit = 90 }: { label: string; value: number; unit: string; warn?: number; crit?: number }) {
  const color = value > crit ? '#ef4444' : value > warn ? '#f59e0b' : '#22c55e'
  return (
    <div style={{ marginBottom: '0.6rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
        <span style={{ color: '#64748b' }}>{label}</span>
        <span style={{ color, fontWeight: 700, fontFamily: 'monospace' }}>{value.toFixed(1)}{unit}</span>
      </div>
      <Bar value={unit === '%' ? value : Math.min(100, (value / (crit * 1.2)) * 100)} warn={warn} crit={crit} />
    </div>
  )
}

export function MetricsPanel({ obs }: Props) {
  if (!obs) return null
  const m = obs.metrics
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>📊 System Metrics</div>
      <Row label="CPU" value={m.cpu_percent} unit="%" />
      <Row label="Memory" value={m.memory_percent} unit="%" />
      <Row label="Latency" value={m.latency_ms} unit="ms" warn={500} crit={2000} />
      <Row label="Error Rate" value={m.error_rate * 100} unit="%" warn={10} crit={30} />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginTop: '0.25rem' }}>
        <span style={{ color: '#475569' }}>Connections</span>
        <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>{m.active_connections}</span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginTop: '0.25rem' }}>
        <span style={{ color: '#475569' }}>Uptime</span>
        <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>{Math.floor(m.uptime_seconds / 3600)}h {Math.floor((m.uptime_seconds % 3600) / 60)}m</span>
      </div>
    </div>
  )
}
