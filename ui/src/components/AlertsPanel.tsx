import React from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

const sevColor = (s: string) => s === 'critical' ? { bg: '#7f1d1d22', border: '#7f1d1d', text: '#fca5a5', label: '#ef4444' }
  : s === 'warning' ? { bg: '#78350f22', border: '#78350f', text: '#fcd34d', label: '#f59e0b' }
  : { bg: '#1e3a5f22', border: '#1e3a5f', text: '#93c5fd', label: '#3b82f6' }

export function AlertsPanel({ obs }: Props) {
  if (!obs || obs.active_alerts.length === 0) return null
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>🚨 Active Alerts ({obs.active_alerts.length})</div>
      {obs.active_alerts.map(a => {
        const c = sevColor(a.severity)
        return (
          <div key={a.id} style={{ background: c.bg, border: `1px solid ${c.border}`, borderRadius: '0.4rem', padding: '0.5rem 0.6rem', marginBottom: '0.4rem' }}>
            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', marginBottom: '0.2rem' }}>
              <span style={{ fontSize: '0.65rem', fontWeight: 800, color: c.label, background: c.label + '22', padding: '0.1rem 0.4rem', borderRadius: '9999px' }}>
                {a.severity.toUpperCase()}
              </span>
              <span style={{ fontSize: '0.72rem', color: '#60a5fa', fontWeight: 600 }}>{a.service}</span>
            </div>
            <p style={{ fontSize: '0.72rem', color: c.text, lineHeight: 1.4 }}>{a.message}</p>
          </div>
        )
      })}
    </div>
  )
}
