import React, { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api'
import type { Observation, Reward, StepResult, Task } from './types'
import { Header } from './components/Header'
import { TaskSelector } from './components/TaskSelector'
import { MetricsPanel } from './components/MetricsPanel'
import { AlertsPanel } from './components/AlertsPanel'
import { LogStream } from './components/LogStream'
import { ActionPanel } from './components/ActionPanel'
import { RewardPanel } from './components/RewardPanel'
import { WorkspacePanel } from './components/WorkspacePanel'
import { Leaderboard } from './components/Leaderboard'
import { TelemetryChart } from './components/TelemetryChart'
import { NoisePanel } from './components/NoisePanel'
import { AgentSwarmPanel } from './components/AgentSwarmPanel'
import { LiveAgentPanel } from './components/LiveAgentPanel'
import { ComparePanel } from './components/ComparePanel'
import { CustomScenarioBuilder } from './components/CustomScenarioBuilder'
import { WarRoom } from './components/WarRoom'
import { ReplayPanel } from './components/ReplayPanel'

export type Tab = 'colosseum' | 'live' | 'compare' | 'warroom' | 'leaderboard' | 'custom' | 'replay'
export interface MetricPoint { step: number; cpu: number; mem: number; err: number; latency: number }

export const panelStyle: React.CSSProperties = {
  background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '0.75rem',
  padding: '0.875rem', marginBottom: '0.75rem',
}
export const titleStyle: React.CSSProperties = {
  fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase',
  letterSpacing: '0.08em', color: '#4b6a9b', marginBottom: '0.625rem',
}

export default function App() {
  const [tab, setTab] = useState<Tab>('colosseum')
  const [tasks, setTasks] = useState<Task[]>([])
  const [activeTask, setActiveTask] = useState('memory_leak')
  const [obs, setObs] = useState<Observation | null>(null)
  const [reward, setReward] = useState<Reward | null>(null)
  const [metricsHistory, setMetricsHistory] = useState<MetricPoint[]>([])
  const [loading, setLoading] = useState(false)
  const [episodeDone, setEpisodeDone] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [actionLog, setActionLog] = useState<Array<{step:number;agent:string;type:string;result:string|null}>>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    api.tasks().then(r => setTasks(r.tasks)).catch(() => {})
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    try {
      const ws = new WebSocket(`${proto}://${window.location.host}/ws`)
      wsRef.current = ws
      ws.onopen = () => setWsConnected(true)
      ws.onclose = () => setWsConnected(false)
      ws.onerror = () => setWsConnected(false)
    } catch {}
    return () => wsRef.current?.close()
  }, [])

  const handleReset = useCallback(async (taskId?: string) => {
    const tid = taskId || activeTask
    setLoading(true); setError(null); setReward(null)
    setEpisodeDone(false); setMetricsHistory([]); setActionLog([])
    try {
      const o = await api.reset(tid)
      setObs(o); setActiveTask(tid)
      setMetricsHistory([{ step: 0, cpu: o.metrics.cpu_percent, mem: o.metrics.memory_percent, err: o.metrics.error_rate * 100, latency: Math.min(o.metrics.latency_ms, 9999) }])
    } catch (e: unknown) { setError(String(e)) }
    finally { setLoading(false) }
  }, [activeTask])

  const handleStep = useCallback(async (action: Record<string, unknown>) => {
    if (!obs || episodeDone) return
    setLoading(true); setError(null)
    try {
      const result: StepResult = await api.step(action)
      const o = result.observation
      setObs(o)
      setMetricsHistory(h => [...h, { step: o.step, cpu: o.metrics.cpu_percent, mem: o.metrics.memory_percent, err: o.metrics.error_rate * 100, latency: Math.min(o.metrics.latency_ms, 9999) }])
      setActionLog(l => [...l, { step: o.step, agent: String(action.agent), type: String(action.action_type), result: o.action_result?.slice(0, 120) || null }])
      if (result.done) { setReward(result.reward); setEpisodeDone(true) }
    } catch (e: unknown) { setError(String(e)) }
    finally { setLoading(false) }
  }, [obs, episodeDone])

  return (
    <div style={{ background: '#080c18', minHeight: '100vh', color: '#e2e8f0', fontFamily: "'Inter','Segoe UI',system-ui,sans-serif" }}>
      <Header tab={tab} setTab={setTab} wsConnected={wsConnected} obs={obs} episodeDone={episodeDone} />

      {tab === 'colosseum' && (
        <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr 300px', gap: '0.875rem', padding: '0.875rem 1.25rem', maxWidth: '1700px', margin: '0 auto' }}>
          <div>
            <TaskSelector tasks={tasks} activeTask={activeTask} onSelect={t => setActiveTask(t)} onReset={handleReset} loading={loading} obs={obs} />
            <MetricsPanel obs={obs} />
            <AlertsPanel obs={obs} />
            <AgentSwarmPanel actionLog={actionLog} />
          </div>
          <div>
            <TelemetryChart data={metricsHistory} />
            <LogStream obs={obs} />
            <NoisePanel obs={obs} />
            <ActionPanel obs={obs} episodeDone={episodeDone} loading={loading} onStep={handleStep} error={error} />
            {obs?.action_result && (
              <div style={panelStyle}>
                <div style={titleStyle}>⚡ Action Result</div>
                <pre style={{ fontSize: '0.72rem', color: '#86efac', fontFamily: 'monospace', whiteSpace: 'pre-wrap', maxHeight: '180px', overflowY: 'auto', lineHeight: 1.5 }}>{obs.action_result}</pre>
              </div>
            )}
            {obs?.action_error && (
              <div style={{ ...panelStyle, borderColor: '#7f1d1d' }}>
                <div style={{ ...titleStyle, color: '#f87171' }}>❌ Error</div>
                <p style={{ fontSize: '0.75rem', color: '#f87171' }}>{obs.action_error}</p>
              </div>
            )}
          </div>
          <div>
            <RewardPanel reward={reward} obs={obs} episodeDone={episodeDone} onReset={() => handleReset()} />
            <WorkspacePanel obs={obs} />
          </div>
        </div>
      )}

      {tab === 'live' && <LiveAgentPanel tasks={tasks} />}
      {tab === 'compare' && <ComparePanel tasks={tasks} />}
      {tab === 'warroom' && <WarRoom tasks={tasks} />}
      {tab === 'leaderboard' && <Leaderboard />}
      {tab === 'custom' && <CustomScenarioBuilder onCreated={() => { api.tasks().then(r => setTasks(r.tasks)).catch(() => {}) }} />}
      {tab === 'replay' && <ReplayPanel />}
    </div>
  )
}
