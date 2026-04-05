import React, { useState } from 'react'
import type { Observation } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props {
  obs: Observation | null
  episodeDone: boolean
  loading: boolean
  onStep: (action: Record<string, unknown>) => void
  error: string | null
}

const AGENTS = ['debugger', 'coder', 'coordinator']
const ACTION_TYPES = ['terminal', 'read_file', 'edit_file', 'list_files', 'search_logs', 'submit_patch', 'escalate']

const QUICK_CMDS = [
  { label: 'tail logs', agent: 'debugger', action_type: 'terminal', command: 'tail -n 20' },
  { label: 'list files', agent: 'debugger', action_type: 'list_files', file_path: '' },
  { label: 'grep ERROR', agent: 'debugger', action_type: 'search_logs', command: 'ERROR' },
  { label: 'grep WARN', agent: 'debugger', action_type: 'search_logs', command: 'WARN' },
  { label: 'htop', agent: 'debugger', action_type: 'terminal', command: 'htop' },
  { label: 'grep deadlock', agent: 'debugger', action_type: 'search_logs', command: 'deadlock' },
  { label: 'grep Redis', agent: 'debugger', action_type: 'search_logs', command: 'Redis' },
  { label: 'grep SECURITY', agent: 'debugger', action_type: 'search_logs', command: 'SECURITY' },
]

const inputStyle: React.CSSProperties = {
  width: '100%', background: '#080c18', border: '1px solid #1e2d4a',
  borderRadius: '0.4rem', padding: '0.45rem 0.6rem', color: '#e2e8f0',
  fontSize: '0.8rem', fontFamily: 'monospace', outline: 'none',
}
const selectStyle: React.CSSProperties = {
  background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem',
  padding: '0.4rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none',
}

export function ActionPanel({ obs, episodeDone, loading, onStep, error }: Props) {
  const [agent, setAgent] = useState('debugger')
  const [actionType, setActionType] = useState('terminal')
  const [command, setCommand] = useState('')
  const [filePath, setFilePath] = useState('')
  const [content, setContent] = useState('')
  const [patchDesc, setPatchDesc] = useState('')

  if (!obs || episodeDone) return null

  const applyQuick = (q: typeof QUICK_CMDS[0]) => {
    setAgent(q.agent)
    setActionType(q.action_type)
    if ('command' in q && q.command !== undefined) setCommand(q.command)
    if ('file_path' in q && q.file_path !== undefined) setFilePath(q.file_path)
  }

  const submit = () => {
    const action: Record<string, unknown> = { agent, action_type: actionType }
    if (command) action.command = command
    if (filePath) action.file_path = filePath
    if (content) action.content = content
    if (patchDesc) action.patch_description = patchDesc
    onStep(action)
  }

  const needsCommand = actionType === 'terminal' || actionType === 'search_logs'
  const needsFile = ['read_file', 'edit_file', 'list_files', 'submit_patch'].includes(actionType)
  const needsContent = actionType === 'edit_file'
  const needsPatch = actionType === 'submit_patch'

  return (
    <div style={panelStyle}>
      <div style={titleStyle}>⚡ Execute Action</div>

      {/* Quick commands */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem', marginBottom: '0.75rem' }}>
        {QUICK_CMDS.map(q => (
          <button key={q.label} onClick={() => applyQuick(q)} style={{
            background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '0.3rem',
            padding: '0.2rem 0.5rem', color: '#64748b', fontSize: '0.68rem', cursor: 'pointer',
            transition: 'all 0.1s',
          }}>
            {q.label}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <div>
          <label style={{ fontSize: '0.68rem', color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Agent</label>
          <select style={selectStyle} value={agent} onChange={e => setAgent(e.target.value)}>
            {AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: '0.68rem', color: '#475569', display: 'block', marginBottom: '0.2rem' }}>Action Type</label>
          <select style={selectStyle} value={actionType} onChange={e => setActionType(e.target.value)}>
            {ACTION_TYPES.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
      </div>

      {needsCommand && (
        <input style={{ ...inputStyle, marginBottom: '0.5rem' }}
          placeholder="command or search pattern"
          value={command} onChange={e => setCommand(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit()} />
      )}
      {needsFile && (
        <input style={{ ...inputStyle, marginBottom: '0.5rem' }}
          placeholder="file path (e.g. api/users.js)"
          value={filePath} onChange={e => setFilePath(e.target.value)} />
      )}
      {needsContent && (
        <textarea style={{ ...inputStyle, height: '120px', marginBottom: '0.5rem', resize: 'vertical' }}
          placeholder="new file content (full fixed code)"
          value={content} onChange={e => setContent(e.target.value)} />
      )}
      {needsPatch && (
        <input style={{ ...inputStyle, marginBottom: '0.5rem' }}
          placeholder="patch description (explain the fix)"
          value={patchDesc} onChange={e => setPatchDesc(e.target.value)} />
      )}

      <button onClick={submit} disabled={loading} style={{
        width: '100%', padding: '0.55rem', border: 'none', borderRadius: '0.5rem',
        background: loading ? '#1e2d4a' : actionType === 'submit_patch' ? 'linear-gradient(135deg,#16a34a,#15803d)' : actionType === 'escalate' ? 'linear-gradient(135deg,#7f1d1d,#991b1b)' : 'linear-gradient(135deg,#1d4ed8,#4f46e5)',
        color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: loading ? 'not-allowed' : 'pointer',
        opacity: loading ? 0.6 : 1, transition: 'opacity 0.15s',
      }}>
        {loading ? '⏳ Executing...' : actionType === 'submit_patch' ? '🚀 Submit Patch' : actionType === 'escalate' ? '🆘 Escalate to Human' : '▶ Execute'}
      </button>

      {error && <div style={{ color: '#f87171', fontSize: '0.72rem', marginTop: '0.4rem', padding: '0.4rem', background: '#7f1d1d22', borderRadius: '0.3rem' }}>{error}</div>}
    </div>
  )
}
