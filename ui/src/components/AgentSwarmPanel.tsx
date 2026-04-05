import React from 'react'
import { panelStyle, titleStyle } from '../App'

interface ActionEntry { step: number; agent: string; type: string; result: string | null }
interface Props { actionLog: ActionEntry[] }

const agentColor = (a: string) => a === 'coordinator' ? '#8b5cf6' : a === 'debugger' ? '#f97316' : '#22c55e'
const agentIcon = (a: string) => a === 'coordinator' ? '🧠' : a === 'debugger' ? '🔍' : '⚙️'

export function AgentSwarmPanel({ actionLog }: Props) {
  if (actionLog.length === 0) return null
  return (
    <div style={panelStyle}>
      <div style={titleStyle}>🤖 Agent Swarm Activity</div>
      <div style={{ maxHeight: '160px', overflowY: 'auto' }}>
        {[...actionLog].reverse().map((entry, i) => (
          <div key={i} style={{ display: 'flex', gap: '0.4rem', padding: '0.3rem 0', borderBottom: '1px solid #0f1629', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.75rem', flexShrink: 0 }}>{agentIcon(entry.agent)}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                <span style={{ fontSize: '0.65rem', fontWeight: 700, color: agentColor(entry.agent) }}>{entry.agent}</span>
                <span style={{ fontSize: '0.65rem', color: '#334155' }}>→</span>
                <span style={{ fontSize: '0.65rem', color: '#475569', fontFamily: 'monospace' }}>{entry.type}</span>
                <span style={{ fontSize: '0.6rem', color: '#1e2d4a', marginLeft: 'auto' }}>s{entry.step}</span>
              </div>
              {entry.result && (
                <div style={{ fontSize: '0.65rem', color: '#334155', fontFamily: 'monospace', marginTop: '0.1rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {entry.result}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
