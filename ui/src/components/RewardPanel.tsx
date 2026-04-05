import React from 'react'
import type { Observation, Reward } from '../types'
import { panelStyle, titleStyle } from '../App'

interface Props {
  reward: Reward | null
  obs: Observation | null
  episodeDone: boolean
  onReset: () => void
}

function RewardBar({ label, value }: { label: string; value: number }) {
  const color = value > 0.7 ? '#22c55e' : value > 0.4 ? '#f59e0b' : '#ef4444'
  return (
    <div style={{ marginBottom: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '0.2rem' }}>
        <span style={{ color: '#64748b' }}>{label}</span>
        <span style={{ color, fontWeight: 700 }}>{(value * 100).toFixed(0)}%</span>
      </div>
      <div style={{ height: 5, background: '#1e2d4a', borderRadius: 3 }}>
        <div style={{ height: '100%', width: `${value * 100}%`, background: color, borderRadius: 3, transition: 'width 0.6s ease' }} />
      </div>
    </div>
  )
}

export function RewardPanel({ reward, obs, episodeDone, onReset }: Props) {
  if (!episodeDone || !reward) {
    // Show live progress hint
    if (!obs) return null
    return (
      <div style={panelStyle}>
        <div style={titleStyle}>🎯 Episode Progress</div>
        <div style={{ textAlign: 'center', padding: '0.5rem 0' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#334155' }}>—</div>
          <div style={{ fontSize: '0.72rem', color: '#334155', marginTop: '0.25rem' }}>Submit a patch to score</div>
        </div>
        {obs.escalated && (
          <div style={{ background: '#78350f22', border: '1px solid #78350f', borderRadius: '0.4rem', padding: '0.5rem', marginTop: '0.5rem' }}>
            <div style={{ fontSize: '0.7rem', color: '#fbbf24', fontWeight: 700, marginBottom: '0.25rem' }}>⚠ Escalated — Max reward: 0.4</div>
            <div style={{ fontSize: '0.68rem', color: '#92400e', lineHeight: 1.4 }}>{obs.escalation_hint}</div>
          </div>
        )}
      </div>
    )
  }

  const score = Math.round(reward.total * 100)
  const scoreColor = score >= 70 ? '#22c55e' : score >= 40 ? '#f59e0b' : '#ef4444'
  const grade = score >= 90 ? 'S' : score >= 70 ? 'A' : score >= 50 ? 'B' : score >= 30 ? 'C' : 'F'

  return (
    <div style={{ ...panelStyle, borderColor: scoreColor + '44' }}>
      <div style={titleStyle}>🏆 Episode Result</div>

      {/* Score */}
      <div style={{ textAlign: 'center', padding: '0.75rem 0 0.5rem' }}>
        <div style={{ fontSize: '3rem', fontWeight: 900, color: scoreColor, lineHeight: 1 }}>
          {score}
          <span style={{ fontSize: '1rem', color: '#334155' }}>/100</span>
        </div>
        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: scoreColor, marginTop: '0.25rem' }}>Grade: {grade}</div>
        <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.4rem', lineHeight: 1.4 }}>{reward.reason}</div>
      </div>

      {/* Breakdown */}
      <div style={{ marginTop: '0.75rem' }}>
        <RewardBar label="Patch Correctness" value={reward.patch_correctness} />
        <RewardBar label="Hidden Tests Passed" value={reward.hidden_tests_passed} />
        <RewardBar label="Step Efficiency" value={reward.steps_efficiency} />
        <RewardBar label="Root Cause ID" value={reward.root_cause_identified} />
        <RewardBar label="No Regression" value={reward.no_regression} />
      </div>

      {reward.escalation_penalty < 0 && (
        <div style={{ fontSize: '0.72rem', color: '#f87171', marginTop: '0.25rem' }}>
          Escalation penalty: {(reward.escalation_penalty * 100).toFixed(0)}%
        </div>
      )}

      {/* Post-mortem */}
      {reward.post_mortem && (
        <div style={{ marginTop: '0.75rem' }}>
          <div style={{ fontSize: '0.68rem', color: '#475569', fontWeight: 700, marginBottom: '0.4rem', textTransform: 'uppercase', letterSpacing: '0.06em' }}>Post-Mortem</div>
          <pre style={{ fontSize: '0.65rem', color: '#475569', fontFamily: 'monospace', whiteSpace: 'pre-wrap', maxHeight: '180px', overflowY: 'auto', background: '#080c18', padding: '0.5rem', borderRadius: '0.4rem', lineHeight: 1.5 }}>
            {JSON.stringify(reward.post_mortem, null, 2)}
          </pre>
        </div>
      )}

      <button onClick={onReset} style={{
        width: '100%', marginTop: '0.75rem', padding: '0.5rem', border: 'none',
        borderRadius: '0.5rem', background: 'linear-gradient(135deg,#1d4ed8,#7c3aed)',
        color: '#fff', fontWeight: 700, fontSize: '0.82rem', cursor: 'pointer',
      }}>
        🔄 Play Again
      </button>
    </div>
  )
}
