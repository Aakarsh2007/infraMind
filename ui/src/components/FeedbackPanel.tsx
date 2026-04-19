import React, { useState } from 'react'
import { panelStyle, titleStyle } from '../App'
import { api } from '../api'

interface Props { runId: string | null; onDone?: () => void }

export function FeedbackPanel({ runId, onDone }: Props) {
  const [rating, setRating] = useState<'thumbs_up'|'thumbs_down'|'neutral'|null>(null)
  const [comment, setComment] = useState('')
  const [correctFix, setCorrectFix] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  if (!runId) return null

  const submit = async () => {
    if (!rating) return
    setLoading(true)
    try {
      await api.submitFeedback({ run_id: runId, rating, comment, correct_fix: correctFix })
      setSubmitted(true)
      onDone?.()
    } catch {}
    finally { setLoading(false) }
  }

  if (submitted) return (
    <div style={{ ...panelStyle, borderColor: '#16a34a44' }}>
      <div style={{ textAlign: 'center', padding: '0.5rem' }}>
        <div style={{ fontSize: '1.5rem' }}>✅</div>
        <div style={{ fontSize: '0.8rem', color: '#22c55e', marginTop: '0.25rem' }}>Feedback recorded! This helps improve the environment.</div>
      </div>
    </div>
  )

  return (
    <div style={{ ...panelStyle, borderColor: '#1e3a5f' }}>
      <div style={titleStyle}>💬 Rate This Run</div>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
        {([['thumbs_up','👍','#22c55e'],['neutral','😐','#f59e0b'],['thumbs_down','👎','#ef4444']] as const).map(([r,icon,color]) => (
          <button key={r} onClick={() => setRating(r)} style={{
            flex: 1, padding: '0.5rem', border: `1px solid ${rating===r ? color : '#1e2d4a'}`,
            borderRadius: '0.4rem', background: rating===r ? color+'22' : 'transparent',
            color: rating===r ? color : '#475569', fontSize: '1.1rem', cursor: 'pointer',
          }}>{icon}</button>
        ))}
      </div>
      <textarea value={comment} onChange={e => setComment(e.target.value)}
        placeholder="What did the agent do well or poorly?"
        style={{ width:'100%', background:'#080c18', border:'1px solid #1e2d4a', borderRadius:'0.4rem', padding:'0.4rem 0.6rem', color:'#e2e8f0', fontSize:'0.75rem', resize:'vertical', height:'60px', marginBottom:'0.5rem' }} />
      <input value={correctFix} onChange={e => setCorrectFix(e.target.value)}
        placeholder="What was the correct fix? (optional)"
        style={{ width:'100%', background:'#080c18', border:'1px solid #1e2d4a', borderRadius:'0.4rem', padding:'0.4rem 0.6rem', color:'#e2e8f0', fontSize:'0.75rem', marginBottom:'0.5rem' }} />
      <button onClick={submit} disabled={!rating || loading} style={{
        width:'100%', padding:'0.45rem', border:'none', borderRadius:'0.4rem',
        background: rating ? 'linear-gradient(135deg,#1d4ed8,#7c3aed)' : '#1e2d4a',
        color:'#fff', fontWeight:700, fontSize:'0.8rem', cursor: rating ? 'pointer' : 'not-allowed',
      }}>{loading ? '...' : 'Submit Feedback'}</button>
    </div>
  )
}
