import React, { useState } from 'react'
import { panelStyle, titleStyle } from '../App'
import { api } from '../api'

interface Props { onCreated: (id: string) => void }

export function CustomScenarioPanel({ onCreated }: Props) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [difficulty, setDifficulty] = useState<'easy'|'medium'|'hard'>('medium')
  const [filePath, setFilePath] = useState('src/buggy.js')
  const [buggyCode, setBuggyCode] = useState('')
  const [fixedCode, setFixedCode] = useState('')
  const [logs, setLogs] = useState('[ERROR] Service crashed')
  const [hint, setHint] = useState('')
  const [patterns, setPatterns] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string|null>(null)

  const submit = async () => {
    if (!name || !buggyCode) return
    setLoading(true)
    try {
      const result = await api.createCustomScenario({
        name, description: desc, difficulty, buggy_file_path: filePath,
        buggy_code: buggyCode, fixed_code: fixedCode,
        initial_logs: logs.split('\n').filter(Boolean),
        root_cause_hint: hint,
        test_patterns: patterns.split(',').map(s => s.trim()).filter(Boolean),
      })
      setResult(`✓ Created: ${(result as any).task_id}`)
      onCreated((result as any).task_id)
    } catch (e) { setResult(`Error: ${e}`) }
    finally { setLoading(false) }
  }

  const inp: React.CSSProperties = { width:'100%', background:'#080c18', border:'1px solid #1e2d4a', borderRadius:'0.4rem', padding:'0.4rem 0.6rem', color:'#e2e8f0', fontSize:'0.75rem', marginBottom:'0.5rem' }

  return (
    <div style={panelStyle}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom: open ? '0.75rem' : 0 }}>
        <div style={titleStyle}>🛠 Custom Scenario</div>
        <button onClick={() => setOpen(o => !o)} style={{ background:'#1e2d4a', border:'none', borderRadius:'0.3rem', padding:'0.2rem 0.6rem', color:'#60a5fa', fontSize:'0.72rem', cursor:'pointer' }}>
          {open ? '▲ Close' : '▼ Build Your Own'}
        </button>
      </div>
      {open && (
        <>
          <input style={inp} placeholder="Scenario name" value={name} onChange={e => setName(e.target.value)} />
          <input style={inp} placeholder="Description" value={desc} onChange={e => setDesc(e.target.value)} />
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem', marginBottom:'0.5rem' }}>
            <select style={{ ...inp, marginBottom:0 }} value={difficulty} onChange={e => setDifficulty(e.target.value as any)}>
              <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
            </select>
            <input style={{ ...inp, marginBottom:0 }} placeholder="File path (e.g. src/app.js)" value={filePath} onChange={e => setFilePath(e.target.value)} />
          </div>
          <textarea style={{ ...inp, height:'100px', resize:'vertical' }} placeholder="Buggy code (paste here)" value={buggyCode} onChange={e => setBuggyCode(e.target.value)} />
          <textarea style={{ ...inp, height:'60px', resize:'vertical' }} placeholder="Initial log lines (one per line)" value={logs} onChange={e => setLogs(e.target.value)} />
          <input style={inp} placeholder="Root cause hint (shown on escalation)" value={hint} onChange={e => setHint(e.target.value)} />
          <input style={inp} placeholder="Test patterns (comma-separated strings that must appear in fix)" value={patterns} onChange={e => setPatterns(e.target.value)} />
          <button onClick={submit} disabled={loading || !name || !buggyCode} style={{ width:'100%', padding:'0.45rem', border:'none', borderRadius:'0.4rem', background:'linear-gradient(135deg,#1d4ed8,#7c3aed)', color:'#fff', fontWeight:700, fontSize:'0.8rem', cursor:'pointer' }}>
            {loading ? '...' : '✓ Create Scenario'}
          </button>
          {result && <div style={{ fontSize:'0.72rem', color: result.startsWith('✓') ? '#22c55e' : '#f87171', marginTop:'0.4rem' }}>{result}</div>}
        </>
      )}
    </div>
  )
}
