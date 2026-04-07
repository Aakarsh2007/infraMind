import React, { useState } from 'react'
import { api } from '../api'
import { panelStyle, titleStyle } from '../App'

interface Props { onCreated: () => void }

const EXAMPLE_BUGGY = `// api/payments.js — Payment processor
const stripe = require('stripe')(process.env.STRIPE_KEY);

// BUG: No idempotency key — duplicate charges on retry
async function chargeCustomer(customerId, amount, currency) {
  const charge = await stripe.charges.create({
    amount,
    currency,
    customer: customerId,
    // Missing: idempotency_key — retries create duplicate charges!
  });
  return charge;
}

module.exports = { chargeCustomer };`

const EXAMPLE_FIXED = `// api/payments.js — Payment processor (FIXED)
const stripe = require('stripe')(process.env.STRIPE_KEY);
const crypto = require('crypto');

// FIX: Add idempotency key to prevent duplicate charges on retry
async function chargeCustomer(customerId, amount, currency, orderId) {
  const idempotencyKey = crypto.createHash('sha256')
    .update(\`\${customerId}-\${orderId}-\${amount}\`)
    .digest('hex');
  
  const charge = await stripe.charges.create({
    amount,
    currency,
    customer: customerId,
  }, {
    idempotencyKey, // Prevents duplicate charges on retry
  });
  return charge;
}

module.exports = { chargeCustomer };`

export function CustomScenarioBuilder({ onCreated }: Props) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium')
  const [buggyFilePath, setBuggyFilePath] = useState('api/payments.js')
  const [buggyCode, setBuggyCode] = useState(EXAMPLE_BUGGY)
  const [fixedCode, setFixedCode] = useState(EXAMPLE_FIXED)
  const [logs, setLogs] = useState('[2026-04-05T10:00:00Z] ERROR duplicate charge detected for customer cus_123\n[2026-04-05T10:00:01Z] ERROR Stripe idempotency violation: charge already exists')
  const [hint, setHint] = useState('The bug is in api/payments.js. Missing idempotency key causes duplicate charges on retry.')
  const [testPatterns, setTestPatterns] = useState('idempotencyKey\nidempotency_key\ncrypto')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const submit = async () => {
    if (!name.trim() || !buggyCode.trim() || !fixedCode.trim()) {
      setError('Name, buggy code, and fixed code are required'); return
    }
    setLoading(true); setError(''); setSuccess('')
    try {
      const result = await api.createCustomScenario({
        name, description, difficulty,
        buggy_file_path: buggyFilePath,
        buggy_code: buggyCode,
        fixed_code: fixedCode,
        initial_logs: logs.split('\n').filter(l => l.trim()),
        root_cause_hint: hint,
        test_patterns: testPatterns.split('\n').filter(p => p.trim()),
      })
      setSuccess(`✓ Scenario "${name}" created! Task ID: ${result.task_id}`)
      onCreated()
    } catch (e: unknown) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const inputStyle: React.CSSProperties = { width: '100%', background: '#080c18', border: '1px solid #1e2d4a', borderRadius: '0.4rem', padding: '0.45rem 0.6rem', color: '#e2e8f0', fontSize: '0.8rem', outline: 'none', marginBottom: '0.5rem' }
  const textareaStyle: React.CSSProperties = { ...inputStyle, fontFamily: 'monospace', fontSize: '0.72rem', resize: 'vertical' }
  const labelStyle: React.CSSProperties = { fontSize: '0.7rem', color: '#475569', display: 'block', marginBottom: '0.2rem' }

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '1.25rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Left — metadata */}
        <div>
          <div style={panelStyle}>
            <div style={titleStyle}>🔧 Custom Scenario Builder</div>
            <div style={{ background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#60a5fa', marginBottom: '0.3rem' }}>How it works</div>
              <p style={{ fontSize: '0.72rem', color: '#64748b', lineHeight: 1.6, marginBottom: '0.3rem' }}>
                1. Paste your buggy code and the fixed version below
              </p>
              <p style={{ fontSize: '0.72rem', color: '#64748b', lineHeight: 1.6, marginBottom: '0.3rem' }}>
                2. Click "Create Scenario" — no API key needed
              </p>
              <p style={{ fontSize: '0.72rem', color: '#64748b', lineHeight: 1.6 }}>
                3. Your scenario appears as a new task — play it in <strong style={{ color: '#94a3b8' }}>Colosseum</strong> or <strong style={{ color: '#94a3b8' }}>Live AI</strong>
              </p>
            </div>

            <label style={labelStyle}>Scenario Name *</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Stripe Duplicate Charges" style={inputStyle} />

            <label style={labelStyle}>Description</label>
            <input value={description} onChange={e => setDescription(e.target.value)} placeholder="What's the incident?" style={inputStyle} />

            <label style={labelStyle}>Difficulty</label>
            <select value={difficulty} onChange={e => setDifficulty(e.target.value as 'easy' | 'medium' | 'hard')} style={{ ...inputStyle, cursor: 'pointer' }}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>

            <label style={labelStyle}>Buggy File Path *</label>
            <input value={buggyFilePath} onChange={e => setBuggyFilePath(e.target.value)} placeholder="api/payments.js" style={inputStyle} />

            <label style={labelStyle}>Escalation Hint (shown when agent escalates)</label>
            <textarea value={hint} onChange={e => setHint(e.target.value)} rows={3} style={textareaStyle} />

            <label style={labelStyle}>Test Patterns (one per line — strings that must appear in the fix)</label>
            <textarea value={testPatterns} onChange={e => setTestPatterns(e.target.value)} rows={4} style={textareaStyle} placeholder="idempotencyKey&#10;crypto&#10;hash" />

            <label style={labelStyle}>Initial Log Lines (one per line)</label>
            <textarea value={logs} onChange={e => setLogs(e.target.value)} rows={4} style={textareaStyle} />

            <button onClick={submit} disabled={loading} style={{ width: '100%', padding: '0.6rem', border: 'none', borderRadius: '0.5rem', background: loading ? '#1e2d4a' : 'linear-gradient(135deg,#16a34a,#15803d)', color: '#fff', fontWeight: 700, fontSize: '0.85rem', cursor: loading ? 'not-allowed' : 'pointer', marginTop: '0.25rem' }}>
              {loading ? '⏳ Creating...' : '🚀 Create Scenario'}
            </button>
            {success && <div style={{ color: '#86efac', fontSize: '0.75rem', marginTop: '0.5rem', padding: '0.5rem', background: '#14532d22', borderRadius: '0.3rem' }}>{success}</div>}
            {error && <div style={{ color: '#f87171', fontSize: '0.75rem', marginTop: '0.5rem', padding: '0.5rem', background: '#7f1d1d22', borderRadius: '0.3rem' }}>{error}</div>}
          </div>
        </div>

        {/* Right — code editors */}
        <div>
          <div style={panelStyle}>
            <div style={titleStyle}>🐛 Buggy Code *</div>
            <textarea value={buggyCode} onChange={e => setBuggyCode(e.target.value)} rows={18}
              style={{ ...textareaStyle, height: '280px', color: '#f87171' }} />
          </div>
          <div style={panelStyle}>
            <div style={titleStyle}>✅ Fixed Code *</div>
            <textarea value={fixedCode} onChange={e => setFixedCode(e.target.value)} rows={18}
              style={{ ...textareaStyle, height: '280px', color: '#86efac' }} />
          </div>
        </div>
      </div>
    </div>
  )
}
