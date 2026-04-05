import React from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

const sourceIcon = (s: string) => s === 'twitter' ? '🐦' : s === 'support_ticket' ? '🎫' : s === 'slack_alert' ? '💬' : s === 'email' ? '📧' : '📢'

export function NoisePanel({ obs }: Props) {
  if (!obs || obs.noise_events.length === 0) return null
  return (
    <div style={{ ...panelStyle, borderColor: '#78350f66' }}>
      <div style={{ ...titleStyle, color: '#f59e0b' }}>⚠ Noise — Filter These Out</div>
      {obs.noise_events.map((n, i) => (
        <div key={i} style={{ display: 'flex', gap: '0.5rem', padding: '0.3rem 0', borderBottom: '1px solid #1e2d4a', alignItems: 'flex-start' }}>
          <span style={{ fontSize: '0.85rem', flexShrink: 0 }}>{sourceIcon(n.source)}</span>
          <div>
            <span style={{ fontSize: '0.65rem', color: '#78350f', fontWeight: 700, textTransform: 'uppercase' }}>{n.source.replace('_', ' ')}</span>
            <p style={{ fontSize: '0.72rem', color: '#92400e', lineHeight: 1.4 }}>{n.content}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
