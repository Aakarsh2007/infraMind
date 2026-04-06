import React, { useState } from 'react'
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
  const [judgeRunning, setJudgeRunning] = useState(false)
  const [judgeResult, setJudgeResult] = useState<string | null>(null)

  const runJudge = async () => {
    setJudgeRunning(true)
    setJudgeResult(null)
    try {
      const r = await fetch('/judge/run_all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed: 42 }),
      })
      const data = await r.json()
      const avg = (data.avg_score * 100).toFixed(1)
      const verdict = data.verdict || ''
      const lines = [`avg: ${avg}% — ${verdict.slice(0, 60)}`]
      for (const [tid, td] of Object.entries(data.tasks || {})) {
        const score = ((td as Record<string, number>).score * 100).toFixed(0)
        lines.push(`${tid.replace('_', ' ')}: ${score}%`)
      }
      setJudgeResult(lines.join('\n'))
    } catch (e) {
      setJudgeResult(`Error: ${e}`)
    } finally {
      setJudgeRunning(false)
    }
  }

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

      {/* Judge Evaluation Button */}
      <button
        onClick={runJudge}
        disabled={judgeRunning}
        style={{
          width: '100%', marginTop: '0.4rem', padding: '0.5rem',
          background: judgeRunning ? '#1e2d4a' : 'linear-gradient(135deg,#16a34a,#15803d)',
          border: 'none', borderRadius: '0.5rem', color: '#fff',
          fontWeight: 700, fontSize: '0.78rem', cursor: judgeRunning ? 'not-allowed' : 'pointer',
          opacity: judgeRunning ? 0.6 : 1,
        }}>
        {judgeRunning ? '⏳ Evaluating...' : '⚖️ Run Judge Evaluation'}
      </button>

      {judgeResult && (
        <div style={{ marginTop: '0.5rem', background: '#080c18', borderRadius: '0.4rem', padding: '0.5rem', border: '1px solid #22c55e33' }}>
          <pre style={{ fontSize: '0.65rem', color: '#86efac', fontFamily: 'monospace', whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
            {judgeResult}
          </pre>
          <a href="/judge/run_all?seed=42" target="_blank" rel="noreferrer"
            style={{ fontSize: '0.65rem', color: '#60a5fa', textDecoration: 'none', display: 'block', marginTop: '0.3rem' }}>
            → Full JSON result ↗
          </a>
        </div>
      )}
    </div>
  )
}
