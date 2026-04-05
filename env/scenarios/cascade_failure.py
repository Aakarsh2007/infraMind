"""
Task 3 — Distributed Cascade Failure (Hard) — 3 randomized variants
"""
from __future__ import annotations
import random, time
from typing import Dict, List, Optional
from env.models import Action, ActionType, Alert, AlertSeverity, ChaosEvent, NoiseEvent, Reward, SystemMetrics
from env.scenarios.base import BaseScenario
from env.scenarios.variants import CASCADE_VARIANTS


class CascadeFailureScenario(BaseScenario):
    task_id = "cascade_failure"
    max_steps = 40

    NOISE_SCHEDULE = {
        1: [NoiseEvent(source="slack_alert", content="Service B is throwing 503s — restart it?")],
        3: [NoiseEvent(source="support_ticket", content="50 users can't log in. Service B is down!")],
        5: [NoiseEvent(source="twitter", content="@YourApp completely broken right now #outage")],
        8: [NoiseEvent(source="email", content="CTO: 'Why is Service B down? Fix Service B NOW'")],
        12: [NoiseEvent(source="slack_alert", content="Service C also failing now — is it a DDoS?")],
        15: [NoiseEvent(source="support_ticket", content="Service B logs show connection pool exhausted")],
        20: [NoiseEvent(source="email", content="Infra team: 'We scaled up Service B — still failing'")],
    }

    def __init__(self, difficulty: float = 1.0) -> None:
        super().__init__(difficulty)
        self._variant = random.choice(CASCADE_VARIANTS)

    def initial_files(self) -> Dict[str, str]:
        files = {
            self._variant["buggy_file"]: self._variant["buggy_code"],
            "service-b/gateway.js": "// service-b — healthy but overwhelmed\nconst express = require('express');\nconst router = express.Router();\nrouter.get('/data/:id', async (req,res) => { res.json({id:req.params.id}); });\nmodule.exports = router;\n",
            "service-c/processor.js": "// service-c — downstream, fails when B is overwhelmed\nconst axios = require('axios');\nasync function process(id) { return axios.get(`http://service-b/data/${id}`); }\nmodule.exports = { process };\n",
            "docker-compose.yml": "version: '3'\nservices:\n  service-a:\n    build: ./service-a\n  service-b:\n    build: ./service-b\n  service-c:\n    build: ./service-c\n  redis:\n    image: redis:7-alpine\n",
        }
        return files

    def initial_logs(self) -> List[str]:
        base = [
            "[2026-04-05T16:00:00Z] INFO  service-a started",
            "[2026-04-05T16:00:01Z] INFO  service-b started",
            "[2026-04-05T16:00:02Z] INFO  service-c started",
            "[2026-04-05T16:05:00Z] ERROR service-b: connection pool exhausted (pool size: 10/10)",
            "[2026-04-05T16:05:01Z] ERROR service-b: GET /data/1001 503 Service Unavailable",
            "[2026-04-05T16:05:10Z] ERROR service-c: upstream service-b timeout after 3000ms",
        ]
        return base + self._variant.get("logs_extra", [])

    def initial_alerts(self) -> List[Alert]:
        return [
            Alert(id="c1", severity=AlertSeverity.CRITICAL, service="service-b",
                  message="Connection pool exhausted — 100% connections in use", timestamp=time.time()),
            Alert(id="c2", severity=AlertSeverity.CRITICAL, service="service-c",
                  message="Upstream timeout rate: 98%", timestamp=time.time()),
            Alert(id="c3", severity=AlertSeverity.WARNING, service="service-a",
                  message=f"Root cause signal: {self._variant['label']}", timestamp=time.time()),
        ]

    def initial_metrics(self) -> SystemMetrics:
        return SystemMetrics(cpu_percent=78.0, memory_percent=61.0, latency_ms=4200.0,
                             error_rate=0.72, active_connections=380, uptime_seconds=14400.0)

    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics:
        prev = self._metrics_history[-1]
        if self.patch_submitted:
            cpu = max(25.0, prev.cpu_percent - 12.0)
            latency = max(80.0, prev.latency_ms / 2.0)
            err = max(0.01, prev.error_rate - 0.15)
        else:
            err = min(0.98, prev.error_rate + 0.02 * self._difficulty)
            cpu = min(98.0, prev.cpu_percent + 1.0)
            latency = min(30000.0, prev.latency_ms * 1.05)
        self._log_buffer.append(f"[METRICS] step={step} cpu={cpu:.1f}% err={err*100:.1f}% latency={latency:.0f}ms")
        if step == 15 and not self.patch_submitted:
            self._log_buffer.append("[CASCADE] service-c: FATAL — all upstream connections failed. Service C is DOWN.")
            self._butterfly_triggered = True
        return SystemMetrics(cpu_percent=round(cpu,1), memory_percent=round(prev.memory_percent,1),
                             latency_ms=round(latency,1), error_rate=round(err,3),
                             active_connections=max(0, 380 - step*8), uptime_seconds=prev.uptime_seconds+30)

    def _check_butterfly(self, step: int, action: Optional[Action]) -> None:
        if action and action.action_type in (ActionType.TERMINAL, ActionType.RESTART_SERVICE):
            cmd = (action.command or "").lower()
            if "service-b" in cmd and ("restart" in cmd or "scale" in cmd):
                self._butterfly_triggered = True
                self._log_buffer.append(f"[BUTTERFLY] step={step}: Service B restarted. Root cause in Service A not fixed — will re-flood in 5 steps.")

    def chaos_event_at(self, step: int) -> Optional[ChaosEvent]:
        if step == 10 and self._difficulty > 1.2:
            return ChaosEvent(step=step, event_type="new_service_failure",
                              description="Service D (reporting) also started failing — unrelated to root cause",
                              impact="Additional noise: Service D 404s flooding logs")
        return None

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        code = self._files.get(self._variant["buggy_file"], patch_content)
        tests = self._variant["tests"]
        passed = sum(1 for _, fn in tests if fn(code))
        fraction = passed / len(tests)
        desc_lower = (patch_description or "").lower()
        root_score = 0.0
        if "service-a" in desc_lower or self._variant["buggy_file"].split("/")[0] in desc_lower:
            root_score += 0.5
        if any(k in desc_lower for k in ["timeout","circuit","backoff","pool","connection"]):
            root_score += 0.5
        steps_bonus = max(0.0, (self.max_steps - self.step_count) / self.max_steps) * 0.15
        no_regression = 1.0 if len(code) > 100 else 0.5
        total = min(1.0, fraction * 0.55 + root_score * 0.15 + steps_bonus + no_regression * 0.1)
        return Reward(
            total=round(total,3), patch_correctness=round(fraction,3),
            hidden_tests_passed=round(fraction,3), steps_efficiency=round(steps_bonus/0.15,3),
            root_cause_identified=round(root_score,3), no_regression=no_regression,
            reason=f"[{self._variant['label']}] Passed {passed}/{len(tests)} tests. Root cause score: {root_score:.1f}",
            post_mortem={"variant": self._variant["id"], "label": self._variant["label"],
                         "root_cause": self._variant["root_cause"],
                         "misleading_signals": ["Service B connection pool", "Service C 503s"],
                         "butterfly_triggered": self._butterfly_triggered,
                         "hidden_tests": {d: fn(code) for d, fn in tests},
                         "agent_steps": self.step_count, "optimal_steps": 18})

    def escalation_hint(self) -> str:
        return self._variant["hint"]

    def memory_hints(self) -> List[str]:
        return getattr(self, '_memory_hints_override', [])
