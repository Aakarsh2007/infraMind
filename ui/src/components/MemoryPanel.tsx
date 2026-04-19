import React, { useEffect, useState } from 'react'
import { panelStyle, titleStyle } from '../App'
import { api } from '../api'

interface MemoryEntry { task_id: string; root_cause: string; fix_summary: string; reward: number; timestamp: number }

export function MemoryPanel() {
  const [entries, setEntries] = useState<MemoryEntry[]>([])

  useEffect(() => {
    api.memory().then((r: any) => setEntries(r.memory || [])).catch(() => {})
    const t = setInterval(() => {
      api.memory().then((r: any) => setEntries(r.memory || [])).catch(() => {})
    }, 5000)
    return () => clearInterval(t)
  }, [])

  if (entries.length === 0) return null

  return (
    <div style={panelStyle}>
      <div style={titleStyle}>🧠 Agent Memory ({entries.length})</div>
      <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
        {entries.slice(0, 8).map((e, i) => (
          <div key={i} style={{ padding: '0.4rem 0', borderBottom: '1px solid #0f1629' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.15rem' }}>
              <span style={{ fontSize: '0.7rem', color: '#60a5fa', fontWeight: 600 }}>{e.task_id.replace('_',' ')}</span>
              <span style={{ fontSize: '0.65rem', color: e.reward >= 0.7 ? '#22c55e' : '#f59e0b', fontFamily: 'monospace' }}>{(e.reward*100).toFixed(0)}%</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#475569', lineHeight: 1.4 }}>{e.fix_summary.slice(0, 100)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
