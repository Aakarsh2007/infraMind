import React from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

const statusColor = (s: string) => s === 'merged' ? '#22c55e' : s === 'approved' ? '#3b82f6' : s === 'changes_requested' ? '#f59e0b' : '#475569'
const statusIcon = (s: string) => s === 'merged' ? '✅' : s === 'approved' ? '✓' : s === 'changes_requested' ? '⚠' : '⏳'

export function PRPanel({ obs }: Props) {
  if (!obs?.pr_review) return null
  const pr = obs.pr_review
  return (
    <div style={{ ...panelStyle, borderColor: statusColor(pr.status) + '44' }}>
      <div style={titleStyle}>🔀 Pull Request</div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#94a3b8', fontFamily: 'monospace' }}>{pr.pr_id}</span>
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: statusColor(pr.status) }}>
          {statusIcon(pr.status)} {pr.status.replace('_', ' ').toUpperCase()}
        </span>
      </div>
      {pr.comments.length > 0 && (
        <div style={{ marginBottom: '0.4rem' }}>
          {pr.comments.map((c, i) => (
            <div key={i} style={{ fontSize: '0.7rem', color: '#64748b', padding: '0.2rem 0', borderBottom: '1px solid #0f1629' }}>💬 {c}</div>
          ))}
        </div>
      )}
      {pr.test_results && (
        <div style={{ fontSize: '0.7rem' }}>
          {Object.entries(pr.test_results).map(([k, v]) => (
            <div key={k} style={{ color: v ? '#22c55e' : '#ef4444' }}>{v ? '✓' : '✗'} {k}</div>
          ))}
        </div>
      )}
    </div>
  )
}
