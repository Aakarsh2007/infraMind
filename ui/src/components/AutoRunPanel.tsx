import React, { useCallback, useRef, useState } from 'react'
import { api } from '../api'
import type { Task } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { tasks: Task[]; onComplete: () => void }

interface RunResult { task_id: string; reward: number; steps: number; status: 'pending' | 'running' | 'done' | 'error'; log: string[] }

const STRATEGIES = [
  { id: 'greedy', label: 'Greedy Debugger', desc: 'Searches logs then reads the most suspicious file and patches it.' },
  { id: 'systematic', label: 'Systematic SRE', desc: 'Lists files, reads all, diagnoses, then patches with full context.' },
  { id: 'fast', label: 'Speed Runner', desc: 'Minimal steps — grep errors, read one file, submit patch immediately.' },
]

function buildActions(taskId: string, strategy: string): Array<Record<string, unknown>> {
  if (strategy === 'fast') {
    return [
      { agent: 'debugger', action_type: 'search_logs', command: 'ERROR' },
      { agent: 'debugger', action_type: 'list_files', file_path: '' },
      { agent: 'coder', action_type: 'read_file', file_path: taskId === 'memory_leak' ? 'api/users.js' : taskId === 'db_deadlock' ? 'services/transfer.js' : taskId === 'cascade_failure' ? 'service-a/cache.js' : taskId === 'cpu_spike' ? 'workers/dataProcessor.js' : 'middleware/auth.js' },
      { agent: 'coder', action_type: 'submit_patch', file_path: taskId === 'memory_leak' ? 'api/users.js' : taskId === 'db_deadlock' ? 'services/transfer.js' : taskId === 'cascade_failure' ? 'service-a/cache.js' : taskId === 'cpu_spike' ? 'workers/dataProcessor.js' : 'middleware/auth.js', patch_description: 'Fast patch attempt' },
    ]
  }
  if (strategy === 'greedy') {
    return [
      { agent: 'debugger', action_type: 'terminal', command: 'tail -n 20' },
      { agent: 'debugger', action_type: 'search_logs', command: 'ERROR' },
      { agent: 'debugger', action_type: 'list_files', file_path: '' },
      { agent: 'coder', action_type: 'read_file', file_path: taskId === 'memory_leak' ? 'api/users.js' : taskId === 'db_deadlock' ? 'services/transfer.js' : taskId === 'cascade_failure' ? 'service-a/cache.js' : taskId === 'cpu_spike' ? 'workers/dataProcessor.js' : 'middleware/auth.js' },
      { agent: 'coder', action_type: 'submit_patch', file_path: taskId === 'memory_leak' ? 'api/users.js' : taskId === 'db_deadlock' ? 'services/transfer.js' : taskId === 'cascade_failure' ? 'service-a/cache.js' : taskId === 'cpu_spike' ? 'workers/dataProcessor.js' : 'middleware/auth.js', patch_description: 'Greedy patch' },
    ]
  }
  // systematic
  return [
    { agent: 'coordinator', action_type: 'terminal', command: 'htop' },
    { agent: 'debugger', action_type: 'terminal', command: 'tail -n 20' },
    { agent: 'debugger', action_type: 'search_logs', command: 'ERROR' },
    { agent: 'debugger', action_type: 'list_files', file_path: '' },
    { agent: 'coder', action_type: 'read_file', file_path: taskId === 'memory_leak' ? 'api/users.js' : taskId === 'db_deadlock' ? 'services/transfer.js' : taskId === 'cascade_failure' ? 'service-a/cache.js' : taskId === 'cpu_spike' ? 'workers/dataProcessor.js' : 'middleware/auth.js' },
    { agent: 'coder', action_type: 'submit_patch', file_path: taskId === 'memory_leak' ? 'api/users.js' : taskId === 'db_deadlock' ? 'services/transfer.js' : taskId === 'cascade_failure' ? 'service-a/cache.js' : taskId === 'cpu_spike' ? 'workers/dataProcessor.js' : 'middleware/auth.js', patch_description: 'Systematic patch after full analysis' },
  ]
}

export function AutoRunPanel({ tasks, onComplete }: Props) {
  const [strategy, setStrategy] = useState('systematic')
  const [selectedTasks, setSelectedTasks] = useState<string[]>(['memory_leak', 'db_deadlock', 'cascade_failure'])
  const [results, setResults] = useState<RunResult[]>([])
  const [running, setRunning] = useState(false)
  const [delay, setDelay] = useState(400)
  const stopRef = useRef(false)

  const toggleTask = (id: string) => setSelectedTasks(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id])

  const runAll = useCallback(async () => {
    setRunning(true)
    stopRef.current = false
    const init: RunResult[] = selectedTasks.map(t => ({ task_id: t, reward: 0, steps: 0, status: 'pending', log: [] }))
    setResults(init)

    for (let i = 0; i < selectedTasks.length; i++) {
      if (stopRef.current) break
      const tid = selectedTasks[i]
      setResults(r => r.map((x, j) => j === i ? { ...x, status: 'running' } : x))

      try {
        await api.reset(tid)
        const actions = buildActions(tid, strategy)
        let lastReward = 0
        let steps = 0
        const log: string[] = [`[START] task=${tid} strategy=${strategy}`]

        for (const action of actions) {
          if (stopRef.current) break
          await new Promise(r => setTimeout(r, delay))
          const result = await api.step(action)
          steps++
          log.push(`[STEP ${steps}] ${action.action_type} → ${result.done ? `DONE reward=${result.reward?.total?.toFixed(3)}` : 'ok'}`)
          setResults(r => r.map((x, j) => j === i ? { ...x, steps, log: [...log] } : x))
          if (result.done) { lastReward = result.reward?.total || 0; break }
        }

        setResults(r => r.map((x, j) => j === i ? { ...x, reward: lastReward, steps, status: 'done', log } : x))
      } catch (e) {
        setResults(r => r.map((x, j) => j === i ? { ...x, status: 'error', log: [`Error: ${e}`] } : x))
      }
    }

    setRunning(false)
    onComplete()
  }, [selectedTasks, strategy, delay, onComplete])

  const avgReward = results.filter(r => r.status === 'done').reduce((s, r) => s + r.reward, 0) / Math.max(1, results.filter(r => r.status === 'done').length)

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '1.25rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Config */}
        <div>
          <div style={panelStyle}>
            <div style={titleStyle}>🤖 Auto-Run Configuration</div>
            <div style={{ marginBottom: '0.75rem' }}>
              <label style={{ fontSize: '0.72rem', color: '#475569', display: 'block', marginBottom: '0.4rem' }}>Strategy</label>
              {STRATEGIES.map(s => (
                <div key={s.id} onClick={() => setStrategy(s.id)} style={{
                  padding: '0.5rem 0.6rem', borderRadius: '0.4rem', cursor: 'pointer', marginBottom: '0.3rem',
                  border: `1px solid ${strategy === s.id ? '#3b82f6' : '#1e2d4a'}`,
                  background: strategy === s.id ? '#1e3a5f22' : 'transparent',
                }}>
                  <div style={{ fontSize: '0.78rem', fontWeight: 700, color: strategy === s.id ? '#60a5fa' : '#64748b' }}>{s.label}</div>
                  <div style={{ fontSize: '0.68rem', color: '#334155' }}>{s.desc}</div>
                </div>
              ))}
            </div>
            <div style={{ marginBottom: '0.75rem' }}>
              <label style={{ fontSize: '0.72rem', color: '#475569', display: 'block', marginBottom: '0.4rem' }}>Tasks to Run</label>
              {tasks.map(t => (
                <label key={t.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.3rem 0', cursor: 'pointer' }}>
                  <input type="checkbox" checked={selectedTasks.includes(t.id)} onChange={() => toggleTask(t.id)} style={{ accentColor: '#3b82f6' }} />
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{t.name}</span>
                </label>
              ))}
            </div>
            <div style={{ marginBottom: '0.75rem' }}>
              <label style={{ fontSize: '0.72rem', color: '#475569', display: 'block', marginBottom: '0.4rem' }}>Step Delay: {delay}ms</label>
              <input type="range" min={100} max={2000} step={100} value={delay} onChange={e => setDelay(Number(e.target.value))} style={{ width: '100%', accentColor: '#3b82f6' }} />
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={runAll} disabled={running || selectedTasks.length === 0} style={{
                flex: 1, padding: '0.55rem', border: 'none', borderRadius: '0.5rem',
                background: running ? '#1e2d4a' : 'linear-gradient(135deg,#1d4ed8,#7c3aed)',
                color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: running ? 'not-allowed' : 'pointer',
              }}>
                {running ? '⏳ Running...' : '▶ Run All Tasks'}
              </button>
              {running && (
                <button onClick={() => { stopRef.current = true }} style={{ padding: '0.55rem 0.75rem', border: '1px solid #7f1d1d', borderRadius: '0.5rem', background: '#7f1d1d22', color: '#f87171', fontSize: '0.82rem', cursor: 'pointer' }}>
                  ⏹ Stop
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Results */}
        <div>
          {results.length > 0 && (
            <div style={panelStyle}>
              <div style={titleStyle}>📊 Run Results</div>
              {results.map((r, i) => {
                const color = r.status === 'done' ? (r.reward >= 0.7 ? '#22c55e' : r.reward >= 0.4 ? '#f59e0b' : '#ef4444') : r.status === 'running' ? '#60a5fa' : r.status === 'error' ? '#ef4444' : '#334155'
                return (
                  <div key={i} style={{ marginBottom: '0.75rem', padding: '0.6rem', background: '#080c18', borderRadius: '0.5rem', border: `1px solid ${color}33` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#94a3b8' }}>{r.task_id.replace('_', ' ')}</span>
                      <span style={{ fontSize: '0.78rem', fontWeight: 800, color, fontFamily: 'monospace' }}>
                        {r.status === 'done' ? `${(r.reward * 100).toFixed(1)}%` : r.status === 'running' ? '⏳' : r.status === 'error' ? '❌' : '—'}
                      </span>
                    </div>
                    {r.status !== 'pending' && (
                      <div style={{ maxHeight: '80px', overflowY: 'auto' }}>
                        {r.log.map((l, j) => (
                          <div key={j} style={{ fontSize: '0.65rem', color: '#334155', fontFamily: 'monospace', lineHeight: 1.4 }}>{l}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
              {results.some(r => r.status === 'done') && (
                <div style={{ textAlign: 'center', padding: '0.5rem', background: '#0f1629', borderRadius: '0.4rem' }}>
                  <div style={{ fontSize: '0.72rem', color: '#475569' }}>Average Reward</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: avgReward >= 0.7 ? '#22c55e' : avgReward >= 0.4 ? '#f59e0b' : '#ef4444' }}>
                    {(avgReward * 100).toFixed(1)}%
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
