import React from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

export function JiraPanel({ obs }: Props) {
  if (!obs || !obs.jira_tickets || obs.jira_tickets.length === 0) return null
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>🎫 Jira Tickets</div>
      {obs.jira_tickets.map(t => (
        <div key={t.id} style={{ padding: '0.4rem 0.5rem', background: '#080c18', borderRadius: '0.4rem', marginBottom: '0.4rem', border: '1px solid #1e2d4a' }}>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.2rem' }}>
            <span style={{ fontSize: '0.65rem', fontWeight: 700, color: '#60a5fa', fontFamily: 'monospace' }}>{t.id}</span>
            <span style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem', borderRadius: '9999px', background: t.status === 'open' ? '#7f1d1d22' : '#14532d22', color: t.status === 'open' ? '#fca5a5' : '#86efac' }}>{t.status}</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{t.title}</div>
          {t.description && <div style={{ fontSize: '0.68rem', color: '#475569', marginTop: '0.15rem' }}>{t.description.slice(0, 80)}</div>}
        </div>
      ))}
    </div>
  )
}
