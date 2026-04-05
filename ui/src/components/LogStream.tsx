import React, { useEffect, useRef, useState } from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { obs: Observation | null }

const lineColor = (l: string) =>
  l.includes('CRITICAL') || l.includes('BREACH') ? '#f43f5e'
  : l.includes('ERROR') ? '#f87171'
  : l.includes('WARN') ? '#fbbf24'
  : l.includes('METRICS') ? '#60a5fa'
  : l.includes('BUTTERFLY') ? '#c084fc'
  : l.includes('CASCADE') ? '#fb923c'
  : l.includes('SECURITY') ? '#f43f5e'
  : l.includes('WORKSPACE') ? '#34d399'
  : '#475569'

export function LogStream({ obs }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  const [filter, setFilter] = useState('')
  const [autoScroll, setAutoScroll] = useState(true)

  useEffect(() => {
    if (autoScroll && ref.current) ref.current.scrollTop = ref.current.scrollHeight
  }, [obs?.recent_logs, autoScroll])

  if (!obs) return null

  const logs = filter
    ? obs.recent_logs.filter(l => l.toLowerCase().includes(filter.toLowerCase()))
    : obs.recent_logs

  return (
    <div style={panelStyle}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <div style={titleStyle}>📟 Log Stream</div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
          <input
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="filter..."
            style={{ background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.3rem', padding: '0.2rem 0.5rem', color: '#94a3b8', fontSize: '0.7rem', width: '100px' }}
          />
          <button onClick={() => setAutoScroll(a => !a)} style={{ background: autoScroll ? '#1e3a5f' : '#1e2d4a', border: 'none', borderRadius: '0.3rem', padding: '0.2rem 0.5rem', color: autoScroll ? '#60a5fa' : '#475569', fontSize: '0.65rem', cursor: 'pointer' }}>
            {autoScroll ? '⬇ AUTO' : '⏸ PAUSED'}
          </button>
        </div>
      </div>
      <div ref={ref} style={{ maxHeight: '200px', overflowY: 'auto', fontFamily: 'monospace' }}>
        {logs.map((l, i) => (
          <div key={i} style={{ fontSize: '0.68rem', padding: '0.1rem 0', color: lineColor(l), lineHeight: 1.5, borderBottom: '1px solid #0f1629' }}>
            {l}
          </div>
        ))}
        {logs.length === 0 && <div style={{ fontSize: '0.7rem', color: '#334155' }}>No matching logs.</div>}
      </div>
    </div>
  )
}
