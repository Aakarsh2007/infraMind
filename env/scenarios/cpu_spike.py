"""
Task 4 — CPU Spike / Infinite Loop (Medium-Hard)
A background job has an accidental infinite loop triggered by a specific
input pattern. CPU hits 100%, the event loop starves, and the service
becomes unresponsive. Inspired by Aegis's C++ probe detecting CPU spikes.
"""
from __future__ import annotations
import time
from typing import Dict, List, Optional
from env.models import Action, Alert, AlertSeverity, NoiseEvent, Reward, SystemMetrics
from env.scenarios.base import BaseScenario

BUGGY_WORKER = """\
// workers/dataProcessor.js — Background data processing worker
const EventEmitter = require('events');
const emitter = new EventEmitter();

// BUG: When input contains a circular reference pattern,
// the sanitize function enters an infinite recursive loop.
function sanitize(obj, depth) {
  // Missing base case — no depth limit check!
  if (typeof obj !== 'object' || obj === null) return obj;
  const result = {};
  for (const key of Object.keys(obj)) {
    result[key] = sanitize(obj[key], depth); // BUG: depth never incremented or checked
  }
  return result;
}

function processRecord(record) {
  // Circular reference in record triggers infinite recursion
  const clean = sanitize(record, 0);
  emitter.emit('processed', clean);
  return clean;
}

// Batch processor — called every 100ms
setInterval(() => {
  const batch = global.__pendingBatch || [];
  global.__pendingBatch = [];
  for (const record of batch) {
    try {
      processRecord(record);
    } catch (e) {
      console.error('Processing error:', e.message);
    }
  }
}, 100);

module.exports = { processRecord, sanitize };
"""

FIXED_WORKER = """\
// workers/dataProcessor.js — Background data processing worker (FIXED)
const EventEmitter = require('events');
const emitter = new EventEmitter();

const MAX_DEPTH = 20;
const seen = new WeakSet();

// FIX: Add depth limit and circular reference detection
function sanitize(obj, depth = 0) {
  if (depth > MAX_DEPTH) return '[MaxDepthExceeded]';
  if (typeof obj !== 'object' || obj === null) return obj;
  if (seen.has(obj)) return '[Circular]';
  seen.add(obj);
  const result = {};
  for (const key of Object.keys(obj)) {
    result[key] = sanitize(obj[key], depth + 1);
  }
  seen.delete(obj);
  return result;
}

function processRecord(record) {
  const clean = sanitize(record, 0);
  emitter.emit('processed', clean);
  return clean;
}

setInterval(() => {
  const batch = global.__pendingBatch || [];
  global.__pendingBatch = [];
  for (const record of batch) {
    try {
      processRecord(record);
    } catch (e) {
      console.error('Processing error:', e.message);
    }
  }
}, 100);

module.exports = { processRecord, sanitize };
"""

HIDDEN_TESTS = [
    ("Depth limit check", lambda c: "MAX_DEPTH" in c or "depth >" in c or "depth>=" in c),
    ("Depth incremented", lambda c: "depth + 1" in c or "depth+1" in c),
    ("Circular reference guard", lambda c: "WeakSet" in c or "Circular" in c or "seen" in c),
    ("Base case returns", lambda c: "return" in c and ("depth" in c or "null" in c)),
    ("Still emits processed event", lambda c: "emit" in c),
]


class CpuSpikeScenario(BaseScenario):
    task_id = "cpu_spike"
    max_steps = 25

    NOISE_SCHEDULE = {
        2: [NoiseEvent(source="slack_alert", content="Infra: 'CPU at 100% — should we add more cores?'")],
        6: [NoiseEvent(source="support_ticket", content="Batch jobs haven't completed in 2 hours")],
        11: [NoiseEvent(source="email", content="Data team: 'Our reports are delayed, is the processor down?'")],
    }

    def initial_files(self) -> Dict[str, str]:
        return {
            "workers/dataProcessor.js": BUGGY_WORKER,
            "workers/scheduler.js": "// scheduler.js — healthy\nconst { processRecord } = require('./dataProcessor');\nmodule.exports = { schedule: (r) => { global.__pendingBatch = global.__pendingBatch || []; global.__pendingBatch.push(r); } };",
            "server.js": "const express = require('express');\nconst { schedule } = require('./workers/scheduler');\nconst app = express();\napp.post('/ingest', (req,res) => { schedule(req.body); res.json({queued:true}); });\napp.listen(3000);\n",
            "package.json": '{"name":"data-processor","version":"1.0.0","dependencies":{"express":"^4.18.0"}}',
        }

    def initial_logs(self) -> List[str]:
        return [
            "[2026-04-05T09:00:00Z] INFO  data-processor started",
            "[2026-04-05T09:01:00Z] INFO  batch processed: 450 records in 98ms",
            "[2026-04-05T09:02:00Z] INFO  batch processed: 512 records in 102ms",
            "[2026-04-05T09:03:00Z] WARN  batch processing time: 4200ms (threshold: 500ms)",
            "[2026-04-05T09:03:05Z] ERROR CPU usage: 99.8% — event loop lag: 8400ms",
            "[2026-04-05T09:03:06Z] ERROR batch processing time: TIMEOUT — worker unresponsive",
            "[2026-04-05T09:03:07Z] ERROR RangeError: Maximum call stack size exceeded",
            "[2026-04-05T09:03:07Z] ERROR   at sanitize (workers/dataProcessor.js:9:18)",
            "[2026-04-05T09:03:07Z] ERROR   at sanitize (workers/dataProcessor.js:9:18)",
            "[2026-04-05T09:03:07Z] ERROR   at sanitize (workers/dataProcessor.js:9:18)",
        ]

    def initial_alerts(self) -> List[Alert]:
        return [
            Alert(id="d1", severity=AlertSeverity.CRITICAL, service="data-processor",
                  message="CPU 99.8% — event loop blocked for 8400ms", timestamp=time.time()),
            Alert(id="d2", severity=AlertSeverity.CRITICAL, service="data-processor",
                  message="RangeError: Maximum call stack size exceeded in sanitize()", timestamp=time.time()),
        ]

    def initial_metrics(self) -> SystemMetrics:
        return SystemMetrics(cpu_percent=99.2, memory_percent=55.0, latency_ms=8400.0,
                             error_rate=0.89, active_connections=12, uptime_seconds=10800.0)

    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics:
        prev = self._metrics_history[-1]
        if self.patch_submitted:
            cpu = max(20.0, prev.cpu_percent - 25.0)
            latency = max(50.0, prev.latency_ms / 4.0)
            err = max(0.01, prev.error_rate - 0.2)
        else:
            cpu = min(100.0, prev.cpu_percent + 0.1)
            latency = min(30000.0, prev.latency_ms + 500.0)
            err = min(0.99, prev.error_rate + 0.01)
        self._log_buffer.append(f"[METRICS] step={step} cpu={cpu:.1f}% latency={latency:.0f}ms err={err*100:.1f}%")
        return SystemMetrics(cpu_percent=round(cpu, 1), memory_percent=round(prev.memory_percent, 1),
                             latency_ms=round(latency, 1), error_rate=round(err, 3),
                             active_connections=max(0, 12 - step), uptime_seconds=prev.uptime_seconds + 30)

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        code = self._files.get("workers/dataProcessor.js", patch_content)
        passed = sum(1 for _, fn in HIDDEN_TESTS if fn(code))
        fraction = passed / len(HIDDEN_TESTS)
        steps_bonus = max(0.0, (self.max_steps - self.step_count) / self.max_steps) * 0.2
        total = min(1.0, fraction * 0.7 + steps_bonus + (0.1 if "emit" in code else 0.0))
        return Reward(total=round(total, 3), patch_correctness=round(fraction, 3),
                      hidden_tests_passed=round(fraction, 3), steps_efficiency=round(steps_bonus / 0.2, 3),
                      root_cause_identified=1.0 if "depth" in (patch_description or "").lower() else 0.3,
                      no_regression=1.0 if "emit" in code else 0.0,
                      reason=f"Passed {passed}/{len(HIDDEN_TESTS)} hidden tests.",
                      post_mortem={"root_cause": "sanitize() missing depth limit and circular ref guard",
                                   "agent_steps": self.step_count, "optimal_steps": 10,
                                   "hidden_tests": {d: fn(code) for d, fn in HIDDEN_TESTS}})

    def escalation_hint(self) -> str:
        return "The infinite loop is in workers/dataProcessor.js. The sanitize() function has no depth limit and no circular reference detection. Add MAX_DEPTH check and a WeakSet to track visited objects."
