"""Custom user-defined scenario."""
from __future__ import annotations
import time
from typing import Dict, List, Optional
from env.models import Alert, AlertSeverity, NoiseEvent, Reward, SystemMetrics
from env.scenarios.base import BaseScenario


class CustomScenario(BaseScenario):
    def __init__(self, config: dict, difficulty: float = 1.0):
        super().__init__(difficulty)
        self._config = config
        self.task_id = config.get("name", "custom").lower().replace(" ", "_")
        self.max_steps = 25

    def initial_files(self) -> Dict[str, str]:
        return {self._config["buggy_file_path"]: self._config["buggy_code"]}

    def initial_logs(self) -> List[str]:
        return list(self._config.get("initial_logs", ["[INFO] Custom scenario started"]))

    def initial_alerts(self) -> List[Alert]:
        return [Alert(id="c1", severity=AlertSeverity.WARNING, service="custom",
                      message=f"Custom incident: {self._config.get('description','')}", timestamp=time.time())]

    def initial_metrics(self) -> SystemMetrics:
        return SystemMetrics(cpu_percent=60.0, memory_percent=55.0, latency_ms=300.0,
                             error_rate=0.15, active_connections=50, uptime_seconds=3600.0)

    def advance_metrics(self, step: int, action) -> SystemMetrics:
        prev = self._metrics_history[-1]
        cpu = min(95.0, prev.cpu_percent + 1.0) if not self.patch_submitted else max(20.0, prev.cpu_percent - 10.0)
        return SystemMetrics(cpu_percent=round(cpu, 1), memory_percent=round(prev.memory_percent, 1),
                             latency_ms=round(prev.latency_ms, 1), error_rate=round(prev.error_rate, 3),
                             active_connections=prev.active_connections, uptime_seconds=prev.uptime_seconds + 30)

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        code = self._files.get(self._config["buggy_file_path"], patch_content)
        patterns = self._config.get("test_patterns", [])
        passed = sum(1 for p in patterns if p.lower() in code.lower()) if patterns else 1
        fraction = passed / max(1, len(patterns))
        steps_bonus = max(0.0, (self.max_steps - self.step_count) / self.max_steps) * 0.2
        total = min(1.0, fraction * 0.7 + steps_bonus)
        return Reward(total=round(total, 3), patch_correctness=round(fraction, 3),
                      hidden_tests_passed=round(fraction, 3), steps_efficiency=round(steps_bonus / 0.2, 3),
                      root_cause_identified=0.5, no_regression=1.0,
                      reason=f"Custom scenario: {passed}/{max(1,len(patterns))} patterns matched.",
                      post_mortem={"root_cause": self._config.get("root_cause_hint", ""),
                                   "agent_steps": self.step_count})

    def escalation_hint(self) -> str:
        return self._config.get("root_cause_hint", "Check the buggy file carefully.")
