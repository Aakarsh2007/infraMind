/// <reference types="vite/client" />
import type { Observation, StepResult, Task } from './types'

const BASE = (import.meta.env.VITE_API_URL as string | undefined) || ''

async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json() as Promise<T>
}

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`)
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json() as Promise<T>
}

export const api = {
  reset: (task_id: string, model = 'manual') => post<Observation>('/reset', { task_id, model }),
  step: (action: Record<string, unknown>) => post<StepResult>('/step', action),
  state: () => get<Record<string, unknown>>('/state'),
  tasks: () => get<{ tasks: Task[] }>('/tasks'),
  leaderboard: () => get<{ leaderboard: unknown[] }>('/leaderboard'),
  stats: () => get<Record<string, unknown>>('/stats'),
  history: () => get<{ history: unknown[] }>('/history'),
  replay: (runId: string) => get<Record<string, unknown>>(`/replay/${runId}`),
  customScenarios: () => get<{ custom_scenarios: string[] }>('/scenarios/custom'),
  createCustomScenario: (body: Record<string, unknown>) => post<Record<string, unknown>>('/scenarios/custom', body),
  memory: () => get<{ memory: unknown[] }>('/memory'),
  submitFeedback: (body: Record<string, unknown>) => post<Record<string, unknown>>('/feedback', body),
}

// SSE helper for live agent streaming
export function createAgentStream(body: Record<string, unknown>, onEvent: (e: Record<string, unknown>) => void, onDone: () => void) {
  const ctrl = new AbortController()
  fetch(`${BASE}/agent/run`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body), signal: ctrl.signal,
  }).then(async res => {
    const reader = res.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) { onDone(); return }
    let buf = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const lines = buf.split('\n')
      buf = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try { onEvent(JSON.parse(line.slice(6))) } catch {}
        }
      }
    }
    onDone()
  }).catch(() => onDone())
  return () => ctrl.abort()
}

export function createCompareStream(body: Record<string, unknown>, onEvent: (e: Record<string, unknown>) => void, onDone: () => void) {
  const ctrl = new AbortController()
  fetch(`${BASE}/agent/compare`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body), signal: ctrl.signal,
  }).then(async res => {
    const reader = res.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) { onDone(); return }
    let buf = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const lines = buf.split('\n')
      buf = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try { onEvent(JSON.parse(line.slice(6))) } catch {}
        }
      }
    }
    onDone()
  }).catch(() => onDone())
  return () => ctrl.abort()
}
