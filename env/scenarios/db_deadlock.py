"""
Task 2 — Database Deadlock (Medium) — 3 randomized variants
"""
from __future__ import annotations
import random, time
from typing import Dict, List, Optional
from env.models import Action, ActionType, Alert, AlertSeverity, ChaosEvent, NoiseEvent, Reward, SystemMetrics
from env.scenarios.base import BaseScenario
from env.scenarios.variants import DB_DEADLOCK_VARIANTS


class DbDeadlockScenario(BaseScenario):
    task_id = "db_deadlock"
    max_steps = 30

    NOISE_SCHEDULE = {
        2: [NoiseEvent(source="support_ticket", content="Payments are failing! Transaction ID 88821 stuck.")],
        5: [NoiseEvent(source="email", content="Finance team: 'We see duplicate charges — is the DB okay?'")],
        10: [NoiseEvent(source="slack_alert", content="DevOps: 'Restarting the service fixed it temporarily'")],
        18: [NoiseEvent(source="twitter", content="Users reporting payment failures. #BankingApp #down")],
    }

    def __init__(self, difficulty: float = 1.0) -> None:
        super().__init__(difficulty)
        self._variant = random.choice(DB_DEADLOCK_VARIANTS)

    def initial_files(self) -> Dict[str, str]:
        files = {
            self._variant["buggy_file"]: self._variant["buggy_code"],
            "db.js": "const { Pool } = require('pg');\nconst pool = new Pool({ connectionString: process.env.DATABASE_URL });\nmodule.exports = { pool };\n",
            "server.js": "const express = require('express');\nconst app = express();\napp.use(express.json());\napp.listen(3000);\n",
            "package.json": '{"name":"payment-service","version":"2.1.0","dependencies":{"express":"^4.18.0","pg":"^8.11.0"}}',
        }
        return files

    def initial_logs(self) -> List[str]:
        base = [
            "[2026-04-05T14:00:00Z] INFO  payment-service started",
            "[2026-04-05T14:01:00Z] INFO  POST /transfer 200 45ms",
            "[2026-04-05T14:02:00Z] ERROR PostgreSQL deadlock detected",
            "[2026-04-05T14:02:01Z] ERROR POST /transfer 500 — deadlock detected",
            "[2026-04-05T14:02:10Z] WARN  error rate: 34% over last 60s",
            "[2026-04-05T14:03:00Z] ERROR deadlock count: 47 in last 5 minutes",
        ]
        return base + self._variant.get("logs_extra", [])

    def initial_alerts(self) -> List[Alert]:
        return [
            Alert(id="b1", severity=AlertSeverity.CRITICAL, service="payment-service",
                  message=f"PostgreSQL deadlock rate: 47/5min [{self._variant['label']}]", timestamp=time.time()),
            Alert(id="b2", severity=AlertSeverity.WARNING, service="payment-service",
                  message="HTTP 500 error rate: 34%", timestamp=time.time()),
        ]

    def initial_metrics(self) -> SystemMetrics:
        return SystemMetrics(cpu_percent=55.0, memory_percent=48.0, latency_ms=890.0,
                             error_rate=0.34, active_connections=210, uptime_seconds=7200.0)

    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics:
        prev = self._metrics_history[-1]
        err = min(0.8, prev.error_rate + 0.03 * self._difficulty) if not self.patch_submitted else max(0.01, prev.error_rate - 0.1)
        cpu = min(90.0, 55.0 + err * 40) if not self.patch_submitted else max(30.0, prev.cpu_percent - 10.0)
        latency = 200.0 + err * 2000
        self._log_buffer.append(f"[METRICS] step={step} cpu={cpu:.1f}% err={err*100:.1f}% latency={latency:.0f}ms")
        if err > 0.5 and not self._butterfly_triggered:
            self._log_buffer.append("[DEADLOCK] 100+ deadlocks/min — DB connection pool exhausted")
        return SystemMetrics(cpu_percent=round(cpu,1), memory_percent=round(prev.memory_percent,1),
                             latency_ms=round(latency,1), error_rate=round(err,3),
                             active_connections=max(0, 210 - step*3), uptime_seconds=prev.uptime_seconds+30)

    def _check_butterfly(self, step: int, action: Optional[Action]) -> None:
        if action and action.action_type in (ActionType.TERMINAL, ActionType.RESTART_SERVICE):
            cmd = (action.command or "").lower()
            if "restart" in cmd or "kill" in cmd or "pm2" in cmd or action.action_type == ActionType.RESTART_SERVICE:
                self._butterfly_triggered = True
                self._log_buffer.append(f"[BUTTERFLY] step={step}: Service restarted. Deadlock will recur in ~5 steps — root cause not fixed.")

    def chaos_event_at(self, step: int) -> Optional[ChaosEvent]:
        if step == 12 and self._difficulty > 1.3:
            return ChaosEvent(step=step, event_type="connection_spike",
                              description="Traffic spike: 3x normal load — deadlock rate tripled",
                              impact="Error rate increased by 20%")
        return None

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        code = self._files.get(self._variant["buggy_file"], patch_content)
        tests = self._variant["tests"]
        passed = sum(1 for _, fn in tests if fn(code))
        fraction = passed / len(tests)
        steps_bonus = max(0.0, (self.max_steps - self.step_count) / self.max_steps) * 0.2
        no_regression = 1.0 if "COMMIT" in code and ("ROLLBACK" in code or "catch" in code) else 0.5
        total = min(1.0, fraction * 0.6 + steps_bonus + no_regression * 0.2)
        desc_lower = (patch_description or "").lower()
        root_id = 1.0 if any(k in desc_lower for k in ["order","ascending","transaction","lock","race","backoff"]) else 0.4
        return Reward(
            total=round(total,3), patch_correctness=round(fraction,3),
            hidden_tests_passed=round(fraction,3), steps_efficiency=round(steps_bonus/0.2,3),
            root_cause_identified=root_id, no_regression=no_regression,
            reason=f"[{self._variant['label']}] Passed {passed}/{len(tests)} hidden tests. Butterfly: {self._butterfly_triggered}",
            post_mortem={"variant": self._variant["id"], "label": self._variant["label"],
                         "root_cause": self._variant["root_cause"],
                         "butterfly_triggered": self._butterfly_triggered,
                         "hidden_tests": {d: fn(code) for d, fn in tests},
                         "agent_steps": self.step_count, "optimal_steps": 12})

    def escalation_hint(self) -> str:
        return self._variant["hint"]

    def memory_hints(self) -> List[str]:
        return getattr(self, '_memory_hints_override', [])
