import React from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import type { MetricPoint } from '../App'
import { panelStyle, titleStyle } from '../App'

interface Props { data: MetricPoint[] }

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.5rem 0.75rem', fontSize: '0.72rem' }}>
      <div style={{ color: '#64748b', marginBottom: '0.25rem' }}>Step {label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ color: p.color }}>{p.name}: {p.value?.toFixed(1)}</div>
      ))}
    </div>
  )
}

export function TelemetryChart({ data }: Props) {
  if (data.length < 2) return null
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>📈 Live Telemetry</div>
      <ResponsiveContainer width="100%" height={150}>
        <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="cpu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="mem" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="err" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2d4a" />
          <XAxis dataKey="step" stroke="#1e2d4a" tick={{ fontSize: 9, fill: '#334155' }} />
          <YAxis stroke="#1e2d4a" tick={{ fontSize: 9, fill: '#334155' }} domain={[0, 100]} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 10, color: '#475569' }} />
          <Area type="monotone" dataKey="cpu" stroke="#f97316" fill="url(#cpu)" dot={false} name="CPU%" strokeWidth={2} />
          <Area type="monotone" dataKey="mem" stroke="#8b5cf6" fill="url(#mem)" dot={false} name="MEM%" strokeWidth={2} />
          <Area type="monotone" dataKey="err" stroke="#ef4444" fill="url(#err)" dot={false} name="ERR%" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
