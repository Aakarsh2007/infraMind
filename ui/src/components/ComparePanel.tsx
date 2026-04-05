import React, { useCallback, useRef, useState } from 'react'
import { createCompareStream } from '../api'
import type { Task } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { tasks: Task[] }

interface CompareStep { side: 'a' | 'b'; step: number; model: string; action_type: string; reasoning: string; metrics: Record<string, number>; done: boolean; reward: number | null }

export function ComparePanel({ tasks }: Props) {
  const [apiKey, setApiKey] = useState('')
  const [modelA, setModelA] = useState('gpt-4o-mini')
  const [modelB, setModelB] = useState('gpt-4o')
  const [taskId, setTaskId] = useState('memory_leak')
  const [maxSteps, setMaxSteps] = useState(15)
  const [running, setRunning] = useState(false)
  const [stepsA, setStepsA] = useState<CompareStep[]>([])
  const [stepsB, setStepsB] = useState<CompareStep[]>([])
  const [metricsA, setMetricsA] = useState<Array<{step:number;cpu:number;err:number}>>([])
  const [metricsB, setMetricsB] = useState<Array<{step:number;cpu:number;err:number}>>([])
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState('')
  const stopRef = useRef<(() => void) | null>(null)

  const start = useCallback(() => {
    if (!apiKey.trim()) { setError('Enter your OpenAI API key'); return }
    setRunning(true); setStepsA([]); setStepsB([]); setMetricsA([]); setMetricsB([]); setResult(null); setError('')

    const stop = createCompareStream(
      { task_id: taskId, model_a: modelA, model_b: modelB, api_key: apiKey, max_steps: maxSteps },
      (event) => {
        if (event.type === 'compare_step') {
          const s = event as unknown as CompareStep
          const m = s.metrics || {}
          if (s.side === 'a') {
            setStepsA(p => [...p, s])
            setMetricsA(p => [...p, { step: s.step, cpu: m.cpu_percent || 0, err: (m.error_rate || 0) * 100 }])
          } else {
            setStepsB(p => [...p, s])
            setMetricsB(p => [...p, { step: s.step, cpu: m.cpu_percent || 0, err: (m.error_rate || 0) * 100 }])
          }
        } else if (event.type === 'compare_complete') {
          setResult(event)
        } else if (event.type === 'error') {
          setError(String(event.message || 'Error'))
        }
      },
      () => { setRunning(false) }
    )
    stopRef.current = stop
  }, [apiKey, modelA, modelB, taskId, maxSteps])

  const winner = result ? String(result.winner || '') : null
  const rewardA = result ? Number(result.reward_a || 0) : null
  const rewardB = result ? Number(result.reward_b || 0) : null

  const StepList = ({ steps, model, color }: { steps: CompareStep[]; model: string; color: string }) => (
    <div style={{ maxHeight: '350px', overflowY: 'auto' }}>
      {steps.map((s, i) => (
        <div key={i} style={{ padding: '0.4rem 0.5rem', borderBottom: '1px solid #0f1629' }}>
          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.65rem', fontWeight: 700, color, fontFamily: 'monospace' }}>s{s.step}</span>
            <span style={{ fontSize: '0.65rem', color: '#475569' }}>{s.action_type}</span>
            {s.done && <span style={{ fontSize: '0.6rem', background: color + '22', color, padding: '0.1rem 0.3rem', borderRadius: '9999px', marginLeft: 'auto' }}>DONE {s.reward !== null ? `${(s.reward * 100).toFixed(0)}%` : ''}</span>}
          </div>
          {s.reasoning && <div style={{ fontSize: '0.62rem', color: '#334155', fontStyle: 'italic', marginTop: '0.1rem' }}>"{s.reasoning}"</div>}
        </div>
      ))}
      {running && steps.length === 0 && <div style={{ padding: '1rem', textAlign: 'center', color: '#334155', fontSize: '0.75rem' }}>Waiting...</div>}
    </div>
  )

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.25rem' }}>
      {/* Config */}
      <div style={{ ...panelStyle, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', alignItems: 'end' }}>
        <div>
          <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>OpenAI API Key</label>
          <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="sk-..."
            style={{ width: '100%', background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }} />
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Model A</label>
          <select value={modelA} onChange={e => setModelA(e.target.value)} style={{ width: '100%', background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }}>
            <option value="gpt-4o-mini">gpt-4o-mini</option><option value="gpt-4o">gpt-4o</option><option value="gpt-4-turbo">gpt-4-turbo</option><option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
          </select>
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Model B</label>
          <select value={modelB} onChange={e => setModelB(e.target.value)} style={{ width: '100%', background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }}>
            <option value="gpt-4o">gpt-4o</option><option value="gpt-4o-mini">gpt-4o-mini</option><option value="gpt-4-turbo">gpt-4-turbo</option><option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
          </select>
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Task</label>
          <select value={taskId} onChange={e => setTaskId(e.target.value)} style={{ width: '100%', background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }}>
            {tasks.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Max Steps: {maxSteps}</label>
          <input type="range" min={5} max={30} value={maxSteps} onChange={e => setMaxSteps(Number(e.target.value))} style={{ width: '100%', accentColor: '#3b82f6' }} />
        </div>
        <button onClick={start} disabled={running} style={{ padding: '0.55rem', border: 'none', borderRadius: '0.5rem', background: running ? '#1e2d4a' : 'linear-gradient(135deg,#1d4ed8,#7c3aed)', color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: running ? 'not-allowed' : 'pointer' }}>
          {running ? '⏳ Running...' : '⚔️ Start Battle'}
        </button>
      </div>
      {error && <div style={{ color: '#f87171', fontSize: '0.75rem', marginBottom: '0.75rem', padding: '0.5rem', background: '#7f1d1d22', borderRadius: '0.4rem' }}>{error}</div>}

      {/* Winner banner */}
      {result && (
        <div style={{ ...panelStyle, textAlign: 'center', borderColor: '#f59e0b44', marginBottom: '1rem' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#f59e0b', marginBottom: '0.25rem' }}>🏆 Winner: {winner}</div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem', fontSize: '0.85rem' }}>
            <span style={{ color: '#60a5fa' }}>{modelA}: {rewardA !== null ? (rewardA * 100).toFixed(1) : '—'}% in {Number(result.steps_a || 0)} steps</span>
            <span style={{ color: '#f97316' }}>{modelB}: {rewardB !== null ? (rewardB * 100).toFixed(1) : '—'}% in {Number(result.steps_b || 0)} steps</span>
          </div>
        </div>
      )}

      {/* Side by side */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div style={panelStyle}>
          <div style={{ ...titleStyle, color: '#60a5fa' }}>🔵 {modelA} {rewardA !== null ? `— ${(rewardA*100).toFixed(0)}%` : ''}</div>
          <StepList steps={stepsA} model={modelA} color="#60a5fa" />
        </div>
        <div style={panelStyle}>
          <div style={{ ...titleStyle, color: '#f97316' }}>🟠 {modelB} {rewardB !== null ? `— ${(rewardB*100).toFixed(0)}%` : ''}</div>
          <StepList steps={stepsB} model={modelB} color="#f97316" />
        </div>
      </div>
    </div>
  )
}
