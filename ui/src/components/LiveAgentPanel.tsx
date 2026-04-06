import React, { useCallback, useRef, useState } from 'react'
import { createAgentStream } from '../api'
import type { Task } from '../types'
import { panelStyle, titleStyle } from '../App'
import { TelemetryChart } from './TelemetryChart'
import type { MetricPoint } from '../App'

interface Props { tasks: Task[] }

interface AgentStep {
  step: number; agent: string; action_type: string; reasoning: string
  action_result: string | null; metrics: Record<string, number>
  logs: string[]; done: boolean; reward: Record<string, unknown> | null
}

const agentColor = (a: string) => a === 'coordinator' ? '#8b5cf6' : a === 'debugger' ? '#f97316' : a === 'coder' ? '#22c55e' : a === 'reviewer' ? '#60a5fa' : '#f43f5e'
const agentIcon = (a: string) => a === 'coordinator' ? '🧠' : a === 'debugger' ? '🔍' : a === 'coder' ? '⚙️' : a === 'reviewer' ? '👁️' : '🚨'

const PROVIDERS = [
  { id: 'openai', label: 'OpenAI', placeholder: 'sk-...', models: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
  { id: 'groq', label: 'Groq (Free)', placeholder: 'gsk_...', models: ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'llama3-70b-8192', 'mixtral-8x7b-32768', 'gemma2-9b-it'] },
]

export function LiveAgentPanel({ tasks }: Props) {
  const [provider, setProvider] = useState('openai')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('gpt-4o-mini')
  const [taskId, setTaskId] = useState('memory_leak')
  const [maxSteps, setMaxSteps] = useState(20)
  const [running, setRunning] = useState(false)
  const [steps, setSteps] = useState<AgentStep[]>([])
  const [metrics, setMetrics] = useState<MetricPoint[]>([])
  const [finalReward, setFinalReward] = useState<Record<string, unknown> | null>(null)
  const [status, setStatus] = useState<'idle' | 'running' | 'done' | 'error'>('idle')
  const [errorMsg, setErrorMsg] = useState('')
  const stopRef = useRef<(() => void) | null>(null)
  const logsRef = useRef<HTMLDivElement>(null)

  const currentProvider = PROVIDERS.find(p => p.id === provider) || PROVIDERS[0]

  const handleProviderChange = (pid: string) => {
    setProvider(pid)
    const p = PROVIDERS.find(x => x.id === pid)
    if (p) setModel(p.models[0])
    setApiKey('')
  }

  const start = useCallback(() => {
    if (!apiKey.trim()) { setErrorMsg(`Enter your ${currentProvider.label} API key first`); return }
    setRunning(true); setSteps([]); setMetrics([]); setFinalReward(null)
    setStatus('running'); setErrorMsg('')

    const stop = createAgentStream(
      { task_id: taskId, api_key: apiKey, model, max_steps: maxSteps },
      (event) => {
        if (event.type === 'reset') {
          const obs = event.observation as Record<string, Record<string, number>>
          const m = obs?.metrics || {}
          setMetrics([{ step: 0, cpu: m.cpu_percent || 0, mem: m.memory_percent || 0, err: (m.error_rate || 0) * 100, latency: Math.min(m.latency_ms || 0, 9999) }])
        } else if (event.type === 'step') {
          const s = event as unknown as AgentStep
          setSteps(prev => [...prev, s])
          const m = s.metrics || {}
          setMetrics(prev => [...prev, { step: s.step, cpu: m.cpu_percent || 0, mem: m.memory_percent || 0, err: (m.error_rate || 0) * 100, latency: Math.min(m.latency_ms || 0, 9999) }])
          if (s.done && s.reward) setFinalReward(s.reward)
          setTimeout(() => { if (logsRef.current) logsRef.current.scrollTop = logsRef.current.scrollHeight }, 50)
        } else if (event.type === 'error') {
          setErrorMsg(String(event.message || 'Unknown error'))
          setStatus('error')
        } else if (event.type === 'complete') {
          setStatus('done')
        }
      },
      () => { setRunning(false); if (status === 'running') setStatus('done') }
    )
    stopRef.current = stop
  }, [apiKey, model, taskId, maxSteps, status, currentProvider])

  const stop = () => { stopRef.current?.(); setRunning(false); setStatus('done') }

  const totalReward = finalReward ? Number(finalReward.total || 0) : null
  const rewardColor = totalReward !== null ? (totalReward >= 0.7 ? '#22c55e' : totalReward >= 0.4 ? '#f59e0b' : '#ef4444') : '#475569'

  const inp: React.CSSProperties = { width: '100%', background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.45rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none', marginBottom: '0.5rem' }
  const sel: React.CSSProperties = { ...inp, cursor: 'pointer' }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.25rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1rem' }}>
        {/* Config */}
        <div>
          <div style={panelStyle}>
            <div style={titleStyle}>🤖 Live AI Agent</div>
            <p style={{ fontSize: '0.72rem', color: '#475569', marginBottom: '0.75rem', lineHeight: 1.5 }}>
              Watch an AI agent solve a real incident live. Your API key is used directly and never stored on the server.
            </p>

            {/* Provider selector */}
            <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Provider</label>
            <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.5rem' }}>
              {PROVIDERS.map(p => (
                <button key={p.id} onClick={() => handleProviderChange(p.id)} style={{
                  flex: 1, padding: '0.4rem', border: `1px solid ${provider === p.id ? '#3b82f6' : '#1e2d4a'}`,
                  borderRadius: '0.4rem', background: provider === p.id ? '#1e3a5f22' : 'transparent',
                  color: provider === p.id ? '#60a5fa' : '#475569', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer',
                }}>
                  {p.label}
                </button>
              ))}
            </div>

            <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>
              {currentProvider.label} API Key
              {provider === 'groq' && <span style={{ color: '#22c55e', marginLeft: '0.4rem', fontSize: '0.65rem' }}>Free tier available at console.groq.com</span>}
            </label>
            <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)}
              placeholder={currentProvider.placeholder} style={inp} />

            <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Model</label>
            <select value={model} onChange={e => setModel(e.target.value)} style={sel}>
              {currentProvider.models.map(m => <option key={m} value={m}>{m}</option>)}
            </select>

            <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Task</label>
            <select value={taskId} onChange={e => setTaskId(e.target.value)} style={sel}>
              {tasks.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>

            <label style={{ fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.25rem' }}>Max Steps: {maxSteps}</label>
            <input type="range" min={5} max={40} value={maxSteps} onChange={e => setMaxSteps(Number(e.target.value))}
              style={{ width: '100%', accentColor: '#3b82f6', marginBottom: '0.75rem' }} />

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={start} disabled={running}
                style={{ flex: 1, padding: '0.55rem', border: 'none', borderRadius: '0.5rem', background: running ? '#1e2d4a' : 'linear-gradient(135deg,#1d4ed8,#7c3aed)', color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: running ? 'not-allowed' : 'pointer' }}>
                {running ? '⏳ Running...' : '▶ Watch AI Solve It'}
              </button>
              {running && (
                <button onClick={stop} style={{ padding: '0.55rem 0.75rem', border: '1px solid #7f1d1d', borderRadius: '0.5rem', background: '#7f1d1d22', color: '#f87171', fontSize: '0.82rem', cursor: 'pointer' }}>⏹</button>
              )}
            </div>
            {errorMsg && <div style={{ color: '#f87171', fontSize: '0.72rem', marginTop: '0.4rem', padding: '0.4rem', background: '#7f1d1d22', borderRadius: '0.3rem' }}>{errorMsg}</div>}
          </div>

          {/* Final reward */}
          {totalReward !== null && (
            <div style={{ ...panelStyle, borderColor: rewardColor + '44', textAlign: 'center' }}>
              <div style={titleStyle}>🏆 Result</div>
              <div style={{ fontSize: '3rem', fontWeight: 900, color: rewardColor }}>{Math.round(totalReward * 100)}<span style={{ fontSize: '1rem', color: '#334155' }}>/100</span></div>
              <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.25rem' }}>{String(finalReward?.reason || '')}</div>
              {finalReward?.post_mortem !== null && finalReward?.post_mortem !== undefined && (
                <div style={{ marginTop: '0.5rem', textAlign: 'left' }}>
                  <div style={{ fontSize: '0.65rem', color: '#334155', fontWeight: 700, marginBottom: '0.25rem' }}>POST-MORTEM</div>
                  <pre style={{ fontSize: '0.62rem', color: '#475569', fontFamily: 'monospace', whiteSpace: 'pre-wrap', maxHeight: '120px', overflowY: 'auto' }}>{JSON.stringify(finalReward.post_mortem, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Live feed */}
        <div>
          <TelemetryChart data={metrics} />
          <div style={panelStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <div style={titleStyle}>🎬 Live Agent Feed</div>
              {running && <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }} />}
              <span style={{ fontSize: '0.68rem', color: '#334155', marginLeft: 'auto' }}>{steps.length} steps</span>
            </div>
            <div ref={logsRef} style={{ maxHeight: '420px', overflowY: 'auto' }}>
              {steps.length === 0 && status === 'idle' && (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#334155' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🤖</div>
                  <div style={{ fontSize: '0.85rem' }}>Configure and click "Watch AI Solve It"</div>
                  <div style={{ fontSize: '0.72rem', color: '#1e2d4a', marginTop: '0.5rem' }}>Works with OpenAI and Groq (free)</div>
                </div>
              )}
              {steps.map((s, i) => (
                <div key={i} style={{ padding: '0.5rem', borderBottom: '1px solid #0f1629', display: 'flex', gap: '0.5rem' }}>
                  <div style={{ flexShrink: 0, width: 24, height: 24, borderRadius: '50%', background: agentColor(s.agent) + '22', border: `1px solid ${agentColor(s.agent)}44`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem' }}>
                    {agentIcon(s.agent)}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', marginBottom: '0.15rem' }}>
                      <span style={{ fontSize: '0.65rem', fontWeight: 700, color: agentColor(s.agent) }}>{s.agent}</span>
                      <span style={{ fontSize: '0.65rem', color: '#475569', fontFamily: 'monospace' }}>{s.action_type}</span>
                      <span style={{ fontSize: '0.6rem', color: '#1e2d4a', marginLeft: 'auto' }}>s{s.step}</span>
                      {s.done && <span style={{ fontSize: '0.6rem', background: '#14532d', color: '#86efac', padding: '0.1rem 0.3rem', borderRadius: '9999px' }}>DONE</span>}
                    </div>
                    {s.reasoning && <div style={{ fontSize: '0.68rem', color: '#64748b', fontStyle: 'italic', marginBottom: '0.15rem' }}>"{s.reasoning}"</div>}
                    {s.action_result && <div style={{ fontSize: '0.65rem', color: '#334155', fontFamily: 'monospace', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.action_result.slice(0, 100)}</div>}
                    {s.done && s.reward && (
                      <div style={{ fontSize: '0.7rem', color: Number(s.reward.total) >= 0.7 ? '#22c55e' : '#f59e0b', fontWeight: 700, marginTop: '0.2rem' }}>
                        Reward: {(Number(s.reward.total) * 100).toFixed(0)}/100
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {running && (
                <div style={{ padding: '0.5rem', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#60a5fa' }} />
                  <span style={{ fontSize: '0.7rem', color: '#475569' }}>Agent thinking...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
