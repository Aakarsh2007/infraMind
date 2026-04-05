"""
Task 1 — Memory Leak (Easy)
3 randomized variants — different bug each run.
"""
from __future__ import annotations
import random, time
from typing import Dict, List, Optional
from env.models import Action, Alert, AlertSeverity, ChaosEvent, NoiseEvent, Reward, SystemMetrics
from env.scenarios.base import BaseScenario
from env.scenarios.variants import MEMORY_LEAK_VARIANTS


class MemoryLeakScenario(BaseScenario):
    task_id = "memory_leak"
    max_steps = 20

    NOISE_SCHEDULE = {
        3: [NoiseEvent(source="support_ticket", content="User #4821 says the app is slow. Please fix ASAP!")],
        7: [NoiseEvent(source="twitter", content="@YourApp your site is DOWN!! #outage #fail")],
        12: [NoiseEvent(source="slack_alert", content="Marketing: 'Can we push the new feature today?'")],
    }

    def __init__(self, difficulty: float = 1.0, seed: Optional[int] = None) -> None:
        super().__init__(difficulty, seed)
        # Pick a random variant using seeded RNG — reproducible per seed
        self._variant = self._rng.choice(MEMORY_LEAK_VARIANTS)

    def initial_files(self) -> Dict[str, str]:
        files = {
            self._variant["buggy_file"]: self._variant["buggy_code"],
            "server.js": "const express = require('express');\nconst app = express();\napp.use(express.json());\napp.listen(3000, () => console.log('Server running'));\n",
            "package.json": '{"name":"sre-service","version":"1.0.0","dependencies":{"express":"^4.18.0","pg":"^8.11.0"}}',
        }
        # Add a healthy decoy file
        files["api/health.js"] = "const express = require('express');\nconst router = express.Router();\nrouter.get('/health', (req,res) => res.json({status:'ok'}));\nmodule.exports = router;\n"
        return files

    def initial_logs(self) -> List[str]:
        base = [
            "[2026-04-05T10:00:01Z] INFO  server started on port 3000",
            "[2026-04-05T10:01:15Z] INFO  GET /api/user/1001 200 12ms",
            "[2026-04-05T10:05:00Z] WARN  heap used: 312MB / 512MB",
            "[2026-04-05T10:08:00Z] WARN  heap used: 398MB / 512MB",
            "[2026-04-05T10:10:00Z] ERROR heap used: 487MB / 512MB — approaching limit",
            "[2026-04-05T10:10:05Z] WARN  GC pressure detected — major collection triggered",
            "[2026-04-05T10:10:10Z] ERROR response latency spike: 1240ms (threshold: 200ms)",
        ]
        return base + self._variant.get("logs_extra", [])

    def initial_alerts(self) -> List[Alert]:
        return [
            Alert(id="a1", severity=AlertSeverity.CRITICAL, service="api",
                  message=f"Memory usage at 95% — OOM imminent [{self._variant['label']}]",
                  timestamp=time.time()),
            Alert(id="a2", severity=AlertSeverity.WARNING, service="api",
                  message="P99 latency > 1000ms", timestamp=time.time()),
        ]

    def initial_metrics(self) -> SystemMetrics:
        base_mem = 65.0 + (self._difficulty - 1.0) * 10
        return SystemMetrics(cpu_percent=42.0, memory_percent=base_mem, latency_ms=320.0,
                             error_rate=0.02, active_connections=145, uptime_seconds=3600.0)

    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics:
        prev = self._metrics_history[-1]
        climb = 3.0 * self._difficulty
        mem = min(99.0, prev.memory_percent + climb) if not self.patch_submitted else max(30.0, prev.memory_percent - 15.0)
        cpu = min(95.0, prev.cpu_percent + 1.5) if mem > 85 else prev.cpu_percent
        latency = 200.0 + (mem - 50) * 20 if mem > 50 else 200.0
        err = min(0.5, (mem - 70) / 100) if mem > 70 else 0.01
        self._log_buffer.append(f"[METRICS] step={step} cpu={cpu:.1f}% mem={mem:.1f}% latency={latency:.0f}ms err={err*100:.1f}%")
        return SystemMetrics(cpu_percent=round(cpu,1), memory_percent=round(mem,1),
                             latency_ms=round(latency,1), error_rate=round(err,3),
                             active_connections=max(0, 145 - step*5), uptime_seconds=prev.uptime_seconds+30)

    def chaos_event_at(self, step: int) -> Optional[ChaosEvent]:
        if step == 8 and self._difficulty > 1.2:
            return ChaosEvent(step=step, event_type="disk_pressure",
                              description="Disk usage hit 90% — swap space activated, making memory issue worse",
                              impact="Memory pressure increased by 10%")
        return None

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        code = self._files.get(self._variant["buggy_file"], patch_content)
        tests = self._variant["tests"]
        passed = sum(1 for _, fn in tests if fn(code))
        fraction = passed / len(tests)
        steps_bonus = max(0.0, (self.max_steps - self.step_count) / self.max_steps) * 0.2
        no_regression = 1.0 if len(code) > 50 else 0.0
        total = min(1.0, fraction * 0.6 + steps_bonus + no_regression * 0.2)
        desc_lower = (patch_description or "").lower()
        root_id = 1.0 if any(k in desc_lower for k in ["cache","leak","evict","listener","release","connection"]) else 0.4
        return Reward(
            total=round(total, 3), patch_correctness=round(fraction, 3),
            hidden_tests_passed=round(fraction, 3), steps_efficiency=round(steps_bonus/0.2, 3),
            root_cause_identified=root_id, no_regression=no_regression,
            reason=f"[{self._variant['label']}] Passed {passed}/{len(tests)} hidden tests.",
            post_mortem={"variant": self._variant["id"], "label": self._variant["label"],
                         "root_cause": self._variant["root_cause"],
                         "optimal_fix": self._variant["optimal_fix"],
                         "hidden_tests": {d: fn(code) for d, fn in tests},
                         "agent_steps": self.step_count, "optimal_steps": 8,
                         "wasted_steps": max(0, self.step_count - 8)})

    def escalation_hint(self) -> str:
        return self._variant["hint"]

    def memory_hints(self) -> List[str]:
        return getattr(self, '_memory_hints_override', [])
