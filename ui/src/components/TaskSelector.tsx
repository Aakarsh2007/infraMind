import React from 'react'
import type { Observation, Task } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props {
  tasks: Task[]
  activeTask: string
  onSelect: (id: string) => void
  onReset: (id: string) => void
  loading: boolean
  obs: Observation | null
}

const diffColor = (d: string) => d === 'easy' ? '#22c55e' : d === 'medium' ? '#f59e0b' : d === 'medium-hard' ? '#f97316' : '#ef4444'
const diffLabel = (d: string) => d === 'easy' ? '🟢' : d === 'medium' ? '🟡' : d === 'medium-hard' ? '🟠' : '🔴'

export function TaskSelector({ tasks, activeTask, onSelect, onReset, loading, obs }: Props) {
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>🎯 Tasks</div>
      {tasks.map(t => (
        <div key={t.id}
          onClick={() => onSelect(t.id)}
          style={{
            padding: '0.6rem 0.75rem', borderRadius: '0.5rem', cursor: 'pointer',
            marginBottom: '0.4rem', transition: 'all 0.15s',
            border: `1px solid ${activeTask === t.id ? diffColor(t.difficulty) + '66' : '#1e2d4a'}`,
            background: activeTask === t.id ? diffColor(t.difficulty) + '12' : 'transparent',
            borderLeft: `3px solid ${diffColor(t.difficulty)}`,
          }}>
          <div style={{ fontSize: '0.78rem', fontWeight: 700, color: activeTask === t.id ? '#e2e8f0' : '#94a3b8', marginBottom: '0.2rem' }}>
            {diffLabel(t.difficulty)} {t.name}
          </div>
          <div style={{ fontSize: '0.68rem', color: '#475569', lineHeight: 1.4 }}>{t.description}</div>
          <div style={{ fontSize: '0.65rem', color: '#334155', marginTop: '0.25rem' }}>
            max {t.max_steps} steps · {t.difficulty}
          </div>
        </div>
      ))}
      <button
        onClick={() => onReset(activeTask)}
        disabled={loading}
        style={{
          width: '100%', marginTop: '0.5rem', padding: '0.55rem',
          background: loading ? '#1e2d4a' : 'linear-gradient(135deg,#1d4ed8,#7c3aed)',
          border: 'none', borderRadius: '0.5rem', color: '#fff',
          fontWeight: 700, fontSize: '0.82rem', cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'opacity 0.15s', opacity: loading ? 0.6 : 1,
        }}>
        {loading ? '⏳ Loading...' : obs ? '🔄 Restart Episode' : '▶ Start Episode'}
      </button>
    </div>
  )
}
