import React, { useEffect, useState } from 'react'
import { api } from '../api'
import { panelStyle, titleStyle } from '../App'

interface RunRecord {
  run_id: string; task_id: string; model: string; reward: number;
  steps: number; escalated: boolean; butterfly_triggered: boolean;
  duration_s: number; timestamp: number;
}

const diffColor = (t: string) => t === 'memory_leak' ? '#22c55e' : t === 'db_deadlock' ? '#f59e0b' : t === 'cascade_failure' ? '#ef4444' : t === 'cpu_spike' ? '#f97316' : '#8b5cf6'
const medal = (i: number) => i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}.`

export function Leaderboard() {
  const [board, setBoard] = useState<RunRecord[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [lb, st] = await Promise.all([api.leaderboard(), api.stats()])
      setBoard((lb.leaderboard as RunRecord[]) || [])
      setStats(st)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '1.25rem' }}>
      {/* Stats cards */}
      {stats && stats.total_runs > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
          {[
            { label: 'Total Runs', value: stats.total_runs, color: '#60a5fa' },
            { label: 'Avg Reward', value: `${(stats.avg_reward * 100).toFixed(1)}%`, color: '#f59e0b' },
            { label: 'Best Reward', value: `${(stats.best_reward * 100).toFixed(1)}%`, color: '#22c55e' },
            { label: 'Tasks', value: Object.keys(stats.by_task || {}).length, color: '#8b5cf6' },
          ].map(s => (
            <div key={s.label} style={{ ...panelStyle, textAlign: 'center', marginBottom: 0 }}>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.2rem' }}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Per-task stats */}
      {stats?.by_task && Object.keys(stats.by_task).length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
          {Object.entries(stats.by_task).map(([tid, ts]: [string, any]) => (
            <div key={tid} style={{ ...panelStyle, marginBottom: 0, borderLeft: `3px solid ${diffColor(tid)}` }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem' }}>{tid.replace('_', ' ')}</div>
              <div style={{ fontSize: '0.8rem', color: diffColor(tid), fontWeight: 700 }}>Best: {(ts.best * 100).toFixed(0)}%</div>
              <div style={{ fontSize: '0.72rem', color: '#475569' }}>Avg: {(ts.avg * 100).toFixed(0)}% · {ts.runs} runs</div>
            </div>
          ))}
        </div>
      )}

      {/* Leaderboard table */}
      <div style={panelStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <div style={titleStyle}>🏆 Leaderboard</div>
          <button onClick={load} style={{ marginLeft: 'auto', background: '#1e2d4a', border: 'none', borderRadius: '0.3rem', padding: '0.25rem 0.6rem', color: '#60a5fa', fontSize: '0.72rem', cursor: 'pointer' }}>
            ↻ Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', color: '#334155', padding: '2rem', fontSize: '0.85rem' }}>Loading...</div>
        ) : board.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#334155', padding: '2rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎮</div>
            <div style={{ fontSize: '0.85rem' }}>No runs yet. Start an episode in the Colosseum!</div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e2d4a' }}>
                  {['Rank', 'Run ID', 'Task', 'Model', 'Reward', 'Steps', 'Escalated', 'Butterfly', 'Duration'].map(h => (
                    <th key={h} style={{ padding: '0.4rem 0.6rem', textAlign: 'left', color: '#334155', fontWeight: 700, fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {board.map((r, i) => {
                  const rewardColor = r.reward >= 0.7 ? '#22c55e' : r.reward >= 0.4 ? '#f59e0b' : '#ef4444'
                  return (
                    <tr key={r.run_id} style={{ borderBottom: '1px solid #0f1629', transition: 'background 0.1s' }}
                      onMouseEnter={e => (e.currentTarget.style.background = '#0f1629')}
                      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
                      <td style={{ padding: '0.5rem 0.6rem', color: '#94a3b8' }}>{medal(i)}</td>
                      <td style={{ padding: '0.5rem 0.6rem', color: '#475569', fontFamily: 'monospace', fontSize: '0.7rem' }}>{r.run_id}</td>
                      <td style={{ padding: '0.5rem 0.6rem' }}>
                        <span style={{ color: diffColor(r.task_id), fontWeight: 600 }}>{r.task_id.replace('_', ' ')}</span>
                      </td>
                      <td style={{ padding: '0.5rem 0.6rem', color: '#64748b', fontFamily: 'monospace', fontSize: '0.7rem' }}>{r.model}</td>
                      <td style={{ padding: '0.5rem 0.6rem' }}>
                        <span style={{ color: rewardColor, fontWeight: 800, fontFamily: 'monospace' }}>{(r.reward * 100).toFixed(1)}%</span>
                      </td>
                      <td style={{ padding: '0.5rem 0.6rem', color: '#64748b', fontFamily: 'monospace' }}>{r.steps}</td>
                      <td style={{ padding: '0.5rem 0.6rem', color: r.escalated ? '#f59e0b' : '#334155' }}>{r.escalated ? '⚠ Yes' : 'No'}</td>
                      <td style={{ padding: '0.5rem 0.6rem', color: r.butterfly_triggered ? '#c084fc' : '#334155' }}>{r.butterfly_triggered ? '🦋 Yes' : 'No'}</td>
                      <td style={{ padding: '0.5rem 0.6rem', color: '#475569', fontFamily: 'monospace' }}>{r.duration_s}s</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
