import React from 'react'
import type { Tab } from '../App'
import type { Observation } from '../types'

interface Props { tab: Tab; setTab: (t: Tab) => void; wsConnected: boolean; obs: Observation | null; episodeDone: boolean }

const TABS: Array<{ id: Tab; label: string }> = [
  { id: 'colosseum', label: '🎮 Colosseum' },
  { id: 'live', label: '🤖 Live AI' },
  { id: 'compare', label: '⚔️ Compare' },
  { id: 'warroom', label: '🚨 War Room' },
  { id: 'leaderboard', label: '🏆 Leaderboard' },
  { id: 'custom', label: '🔧 Custom' },
  { id: 'replay', label: '📼 Replay' },
]

const pressureColor = (p: string) => p === 'critical' ? '#ef4444' : p === 'elevated' ? '#f59e0b' : '#22c55e'

export function Header({ tab, setTab, wsConnected, obs, episodeDone }: Props) {
  return (
    <div style={{ background: 'linear-gradient(135deg,#080c18 0%,#0f1629 100%)', borderBottom: '1px solid #1e2d4a', padding: '0 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', height: '52px', position: 'sticky', top: 0, zIndex: 100, overflowX: 'auto' }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginRight: '0.5rem', flexShrink: 0 }}>
        <span style={{ fontSize: '1.3rem' }}>⚔️</span>
        <span style={{ fontSize: '1rem', fontWeight: 800, background: 'linear-gradient(135deg,#f97316,#ef4444,#8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', whiteSpace: 'nowrap' }}>Gravex-Aegis</span>
      </div>

      {TABS.map(t => (
        <button key={t.id} onClick={() => setTab(t.id)} style={{ background: tab === t.id ? '#1e2d4a' : 'transparent', border: tab === t.id ? '1px solid #2d4a7a' : '1px solid transparent', borderRadius: '0.4rem', padding: '0.3rem 0.65rem', color: tab === t.id ? '#93c5fd' : '#475569', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600, transition: 'all 0.15s', whiteSpace: 'nowrap', flexShrink: 0 }}>
          {t.label}
        </button>
      ))}

      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.6rem', flexShrink: 0 }}>
        {obs && (
          <>
            <span style={{ fontSize: '0.68rem', color: '#334155' }}>Step {obs.step}</span>
            <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '0.15rem 0.5rem', borderRadius: '9999px', border: `1px solid ${pressureColor(obs.time_pressure)}44`, background: pressureColor(obs.time_pressure) + '18', color: pressureColor(obs.time_pressure) }}>
              {obs.time_pressure.toUpperCase()}
            </span>
          </>
        )}
        {episodeDone && <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '0.15rem 0.5rem', borderRadius: '9999px', background: '#14532d', color: '#86efac', border: '1px solid #16a34a44' }}>✓ DONE</span>}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.65rem', color: wsConnected ? '#22c55e' : '#475569' }}>
          <div style={{ width: 5, height: 5, borderRadius: '50%', background: wsConnected ? '#22c55e' : '#475569', boxShadow: wsConnected ? '0 0 5px #22c55e' : 'none' }} />
          {wsConnected ? 'LIVE' : 'OFFLINE'}
        </div>
      </div>
    </div>
  )
}
