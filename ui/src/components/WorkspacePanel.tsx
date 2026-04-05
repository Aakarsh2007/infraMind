import React from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

const fileIcon = (f: string) => f.endsWith('.js') ? '🟨' : f.endsWith('.ts') ? '🔷' : f.endsWith('.json') ? '📋' : f.endsWith('.yml') || f.endsWith('.yaml') ? '⚙️' : '📄'

export function WorkspacePanel({ obs }: Props) {
  if (!obs || obs.available_files.length === 0) return null
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>📁 Workspace Files</div>
      {obs.available_files.map(f => (
        <div key={f} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.3rem 0.4rem', borderRadius: '0.3rem', cursor: 'pointer', transition: 'background 0.1s' }}
          onMouseEnter={e => (e.currentTarget.style.background = '#1e2d4a')}
          onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
          <span style={{ fontSize: '0.75rem' }}>{fileIcon(f)}</span>
          <span style={{ fontSize: '0.72rem', color: '#60a5fa', fontFamily: 'monospace' }}>{f}</span>
        </div>
      ))}
    </div>
  )
}
