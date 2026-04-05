import React, { useEffect, useState } from 'react'
import { api } from '../api'
import { panelStyle, titleStyle } from '../App'

export function ReplayPanel() {
  const [history, setHistory] = useState<Record<string, unknown>[]>([])
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.history().then(r => {
      setHistory((r.history as Record<string, unknown>[]) || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const loadReplay = async (runId: string) => {
    try {
      const data = await api.replay(runId)
      setSelected(data)
    } catch {}
  }

  const diffColor = (t: string) => t === 'memory_leak' ? '#22c55e' : t === 'db_deadlock' ? '#f59e0b' : t === 'cascade_failure' ? '#ef4444' : t === 'cpu_spike' ? '#f97316' : '#8b5cf6'

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '1.25rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '1rem' }}>
        {/* Run list */}
        <div style={panelStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <div style={titleStyle}>📼 Run History</div>
            <button onClick={() => { setLoading(true); api.history().then(r => setHistory((r.history as Record<string, unknown>[]) || [])).finally(() => setLoading(false)) }}
              style={{ marginLeft: 'auto', background: '#1e2d4a', border: 'none', borderRadius: '0.3rem', padding: '0.2rem 0.5rem', color: '#60a5fa', fontSize: '0.7rem', cursor: 'pointer' }}>↻</button>
          </div>
          {loading ? (
            <div style={{ textAlign: 'center', color: '#334155', padding: '2rem', fontSize: '0.8rem' }}>Loading...</div>
          ) : history.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#334155', padding: '2rem' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📼</div>
              <div style={{ fontSize: '0.8rem' }}>No runs yet. Complete an episode to see replays.</div>
            </div>
          ) : (
            <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
              {history.map((run, i) => {
                const reward = Number(run.reward || 0)
                const rewardColor = reward >= 0.7 ? '#22c55e' : reward >= 0.4 ? '#f59e0b' : '#ef4444'
                const isSelected = selected?.run_id === run.run_id
                return (
                  <div key={i} onClick={() => loadReplay(String(run.run_id))}
                    style={{ padding: '0.6rem', borderRadius: '0.4rem', cursor: 'pointer', marginBottom: '0.3rem', border: `1px solid ${isSelected ? '#3b82f6' : '#1e2d4a'}`, background: isSelected ? '#1e3a5f22' : 'transparent', transition: 'all 0.15s' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: diffColor(String(run.task_id)) }}>{String(run.task_id).replace('_', ' ')}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 800, color: rewardColor, fontFamily: 'monospace' }}>{(reward * 100).toFixed(0)}%</span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.65rem', color: '#475569' }}>
                      <span>#{String(run.run_id)}</span>
                      <span>{Number(run.steps)} steps</span>
                      <span>{String(run.model)}</span>
                      {Boolean(run.butterfly_triggered) && <span style={{ color: '#c084fc' }}>🦋</span>}
                      {Boolean(run.escalated) && <span style={{ color: '#f59e0b' }}>⚠</span>}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Replay detail */}
        <div>
          {!selected ? (
            <div style={{ ...panelStyle, textAlign: 'center', padding: '3rem' }}>
              <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>📼</div>
              <div style={{ fontSize: '0.9rem', color: '#475569' }}>Select a run to view its replay</div>
            </div>
          ) : (
            <div style={panelStyle}>
              <div style={titleStyle}>📼 Replay — Run #{String(selected.run_id)}</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem', marginBottom: '0.75rem' }}>
                {[
                  { label: 'Task', value: String(selected.task_id).replace('_', ' ') },
                  { label: 'Reward', value: `${(Number(selected.reward || 0) * 100).toFixed(1)}%` },
                  { label: 'Steps', value: String(selected.steps) },
                  { label: 'Duration', value: `${Number(selected.duration_s || 0).toFixed(1)}s` },
                ].map(s => (
                  <div key={s.label} style={{ background: '#080c18', borderRadius: '0.4rem', padding: '0.5rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.65rem', color: '#475569' }}>{s.label}</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#e2e8f0' }}>{s.value}</div>
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                {Boolean(selected.butterfly_triggered) && <span style={{ fontSize: '0.7rem', background: '#c084fc22', color: '#c084fc', padding: '0.2rem 0.5rem', borderRadius: '9999px', border: '1px solid #c084fc44' }}>🦋 Butterfly Triggered</span>}
                {Boolean(selected.escalated) && <span style={{ fontSize: '0.7rem', background: '#f59e0b22', color: '#f59e0b', padding: '0.2rem 0.5rem', borderRadius: '9999px', border: '1px solid #f59e0b44' }}>⚠ Escalated</span>}
                <span style={{ fontSize: '0.7rem', background: '#1e2d4a', color: '#64748b', padding: '0.2rem 0.5rem', borderRadius: '9999px' }}>Model: {String(selected.model)}</span>
              </div>

              {selected.post_mortem !== null && selected.post_mortem !== undefined && (
                <div>
                  <div style={{ fontSize: '0.68rem', color: '#475569', fontWeight: 700, marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Post-Mortem Report</div>
                  <pre style={{ fontSize: '0.68rem', color: '#64748b', fontFamily: 'monospace', whiteSpace: 'pre-wrap', background: '#080c18', padding: '0.75rem', borderRadius: '0.4rem', maxHeight: '300px', overflowY: 'auto', lineHeight: 1.6 }}>
                    {JSON.stringify(selected.post_mortem, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
