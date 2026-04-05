import React, { useCallback, useRef, useState } from 'react'
import { createAgentStream } from '../api'
import type { Task } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props { tasks: Task[] }

interface Message { from: string; to: string; content: string; step: number; type: 'action' | 'reasoning' | 'result' | 'alert' }

const AGENTS = [
  { id: 'coordinator', label: 'Coordinator', icon: '🧠', color: '#8b5cf6', role: 'Delegates tasks, synthesizes findings' },
  { id: 'debugger', label: 'Debugger', icon: '🔍', color: '#f97316', role: 'Reads logs, runs terminal commands' },
  { id: 'coder', label: 'Coder', icon: '⚙️', color: '#22c55e', role: 'Reads/edits files, submits patches' },
  { id: 'reviewer', label: 'Reviewer', icon: '👁️', color: '#60a5fa', role: 'Validates patches, runs tests' },
  { id: 'sre', label: 'SRE', icon: '🚨', color: '#f43f5e', role: 'Monitors metrics, creates Jira tickets' },
]

export function WarRoom({ tasks }: Props) {
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('gpt-4o-mini')
  const [taskId, setTaskId] = useState('cascade_failure')
  const [running, setRunning] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [activeAgents, setActiveAgents] = useState<Set<string>>(new Set())
  const [finalReward, setFinalReward] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  const stopRef = useRef<(() => void) | null>(null)
  const feedRef = useRef<HTMLDivElement>(null)

  const start = useCallback(() => {
    if (!apiKey.trim()) { setError('Enter your OpenAI API key'); return }
    setRunning(true); setMessages([]); setActiveAgents(new Set()); setFinalReward(null); setError(''); setCurrentStep(0)

    const stop = createAgentStream(
      { task_id: taskId, api_key: apiKey, model, max_steps: 25 },
      (event) => {
        if (event.type === 'step') {
          const agent = String(event.agent || 'debugger')
          const actionType = String(event.action_type || '')
          const reasoning = String(event.reasoning || '')
          const result = event.action_result ? String(event.action_result).slice(0, 120) : null
          const step = Number(event.step || 0)
          setCurrentStep(step)
          setActiveAgents(prev => new Set([...prev, agent]))

          const msgs: Message[] = []
          if (reasoning) msgs.push({ from: agent, to: 'all', content: `[Thinking] ${reasoning}`, step, type: 'reasoning' })
          msgs.push({ from: agent, to: 'system', content: `→ ${actionType}${result ? `: ${result}` : ''}`, step, type: 'action' })

          // Simulate inter-agent messages
          if (actionType === 'search_logs' && result) {
            msgs.push({ from: agent, to: 'coordinator', content: `Found in logs: ${result.slice(0, 80)}`, step, type: 'result' })
          }
          if (actionType === 'submit_patch') {
            msgs.push({ from: agent, to: 'reviewer', content: 'Patch submitted — please review', step, type: 'action' })
            msgs.push({ from: 'reviewer', to: agent, content: 'Running hidden test suite...', step, type: 'result' })
          }
          if (event.done && event.reward) {
            const r = event.reward as Record<string, unknown>
            setFinalReward(Number(r.total || 0))
            msgs.push({ from: 'coordinator', to: 'all', content: `Episode complete! Reward: ${(Number(r.total || 0) * 100).toFixed(0)}/100`, step, type: 'alert' })
          }

          setMessages(prev => [...prev, ...msgs])
          setTimeout(() => { if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight }, 50)
        } else if (event.type === 'error') {
          setError(String(event.message || 'Error'))
        }
      },
      () => { setRunning(false) }
    )
    stopRef.current = stop
  }, [apiKey, model, taskId])

  const agentColor = (id: string) => AGENTS.find(a => a.id === id)?.color || '#475569'
  const agentIcon = (id: string) => AGENTS.find(a => a.id === id)?.icon || '🤖'

  const msgBg = (type: string) => type === 'reasoning' ? '#1e2d4a22' : type === 'alert' ? '#78350f22' : type === 'result' ? '#14532d22' : '#0f1629'
  const msgColor = (type: string) => type === 'reasoning' ? '#64748b' : type === 'alert' ? '#fbbf24' : type === 'result' ? '#86efac' : '#94a3b8'

  return (
    <div style={{ maxWidth: '1300px', margin: '0 auto', padding: '1.25rem' }}>
      {/* Config bar */}
      <div style={{ ...panelStyle, display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={titleStyle}>⚔️ War Room</div>
        <input type="password" value={apiKey} onChange={e => setApiKey(e.target.value)} placeholder="OpenAI API Key (sk-...)"
          style={{ flex: 1, minWidth: 200, background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }} />
        <select value={model} onChange={e => setModel(e.target.value)} style={{ background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }}>
          <option value="gpt-4o-mini">gpt-4o-mini</option><option value="gpt-4o">gpt-4o</option>
        </select>
        <select value={taskId} onChange={e => setTaskId(e.target.value)} style={{ background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none' }}>
          {tasks.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        <button onClick={start} disabled={running} style={{ padding: '0.5rem 1.25rem', border: 'none', borderRadius: '0.5rem', background: running ? '#1e2d4a' : 'linear-gradient(135deg,#1d4ed8,#7c3aed)', color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: running ? 'not-allowed' : 'pointer' }}>
          {running ? `⏳ Step ${currentStep}` : '🚀 Launch War Room'}
        </button>
        {running && <button onClick={() => { stopRef.current?.(); setRunning(false) }} style={{ padding: '0.5rem 0.75rem', border: '1px solid #7f1d1d', borderRadius: '0.5rem', background: '#7f1d1d22', color: '#f87171', fontSize: '0.82rem', cursor: 'pointer' }}>⏹</button>}
        {error && <span style={{ color: '#f87171', fontSize: '0.72rem' }}>{error}</span>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '1rem' }}>
        {/* Agent roster */}
        <div>
          <div style={panelStyle}>
            <div style={titleStyle}>👥 Agent Team</div>
            {AGENTS.map(a => (
              <div key={a.id} style={{ padding: '0.5rem', borderRadius: '0.4rem', marginBottom: '0.4rem', background: activeAgents.has(a.id) ? a.color + '18' : 'transparent', border: `1px solid ${activeAgents.has(a.id) ? a.color + '44' : '#1e2d4a'}`, transition: 'all 0.3s' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span style={{ fontSize: '1rem' }}>{a.icon}</span>
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: activeAgents.has(a.id) ? a.color : '#64748b' }}>{a.label}</div>
                    <div style={{ fontSize: '0.62rem', color: '#334155' }}>{a.role}</div>
                  </div>
                  {activeAgents.has(a.id) && running && (
                    <div style={{ marginLeft: 'auto', width: 6, height: 6, borderRadius: '50%', background: a.color, boxShadow: `0 0 6px ${a.color}` }} />
                  )}
                </div>
              </div>
            ))}
            {finalReward !== null && (
              <div style={{ marginTop: '0.75rem', textAlign: 'center', padding: '0.5rem', background: '#0f1629', borderRadius: '0.4rem' }}>
                <div style={{ fontSize: '0.7rem', color: '#475569' }}>Team Score</div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: finalReward >= 0.7 ? '#22c55e' : finalReward >= 0.4 ? '#f59e0b' : '#ef4444' }}>{Math.round(finalReward * 100)}</div>
              </div>
            )}
          </div>
        </div>

        {/* War room feed */}
        <div style={panelStyle}>
          <div style={titleStyle}>📡 War Room Feed</div>
          <div ref={feedRef} style={{ maxHeight: '520px', overflowY: 'auto' }}>
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', padding: '3rem', color: '#334155' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>⚔️</div>
                <div>Launch the War Room to see agents coordinate in real time</div>
              </div>
            )}
            {messages.map((msg, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.5rem', padding: '0.4rem 0.5rem', borderBottom: '1px solid #0f1629', background: msgBg(msg.type) }}>
                <div style={{ flexShrink: 0, fontSize: '0.85rem' }}>{agentIcon(msg.from)}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', marginBottom: '0.1rem' }}>
                    <span style={{ fontSize: '0.65rem', fontWeight: 700, color: agentColor(msg.from) }}>{msg.from}</span>
                    {msg.to !== 'all' && msg.to !== 'system' && (
                      <>
                        <span style={{ fontSize: '0.6rem', color: '#334155' }}>→</span>
                        <span style={{ fontSize: '0.65rem', color: agentColor(msg.to) }}>{msg.to}</span>
                      </>
                    )}
                    <span style={{ fontSize: '0.6rem', color: '#1e2d4a', marginLeft: 'auto' }}>s{msg.step}</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: msgColor(msg.type), lineHeight: 1.4 }}>{msg.content}</div>
                </div>
              </div>
            ))}
            {running && (
              <div style={{ padding: '0.5rem', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: 3 }}>
                  {[0,1,2].map(i => <div key={i} style={{ width: 4, height: 4, borderRadius: '50%', background: '#60a5fa', opacity: 0.6 + i * 0.2 }} />)}
                </div>
                <span style={{ fontSize: '0.7rem', color: '#475569' }}>Agents coordinating...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
