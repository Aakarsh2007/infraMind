"""
Base scenario — complete implementation with all features:
butterfly effect, chaos injection, agent communication,
PR review simulation, CI/CD, Jira tickets, memory hints,
explainability scoring, safety layer, dynamic difficulty.
"""
from __future__ import annotations
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from env.models import (
    Action, ActionType, AgentRole, Alert, AlertSeverity,
    AgentMessage, ChaosEvent, JiraTicket, NoiseEvent,
    Observation, PRReview, Reward, SystemMetrics,
)


class BaseScenario(ABC):
    task_id: str = ""
    max_steps: int = 20
    NOISE_SCHEDULE: Dict[int, List[NoiseEvent]] = {}
    CHAOS_STEPS: List[int] = []  # Steps where chaos is injected

    def __init__(self, difficulty: float = 1.0) -> None:
        self.step_count = 0
        self.done = False
        self.escalated = False
        self.patch_submitted = False
        self.escalation_hint_given = False
        self.agent_messages: List[AgentMessage] = []
        self._log_buffer: List[str] = []
        self._files: Dict[str, str] = {}
        self._metrics_history: List[SystemMetrics] = []
        self._butterfly_triggered = False
        self._patch_content: Optional[str] = None
        self._patch_description: Optional[str] = None
        self._reset_time = time.time()
        self._chaos_events: List[ChaosEvent] = []
        self._jira_tickets: List[JiraTicket] = []
        self._pr_review: Optional[PRReview] = None
        self._ci_status: Optional[str] = None
        self._reasoning_log: List[str] = []
        self._destructive_actions = 0
        self._collaboration_actions = 0
        self._difficulty = max(0.5, min(2.0, difficulty))
        self._restart_count = 0

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def initial_files(self) -> Dict[str, str]: ...
    @abstractmethod
    def initial_logs(self) -> List[str]: ...
    @abstractmethod
    def initial_alerts(self) -> List[Alert]: ...
    @abstractmethod
    def initial_metrics(self) -> SystemMetrics: ...
    @abstractmethod
    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics: ...
    @abstractmethod
    def grade_patch(self, patch_content: str, patch_description: str) -> Reward: ...
    @abstractmethod
    def escalation_hint(self) -> str: ...

    def initial_jira_tickets(self) -> List[JiraTicket]:
        return [JiraTicket(id=f"{self.task_id.upper()[:3]}-001",
                           title=f"Production incident: {self.task_id.replace('_',' ')}",
                           description="Service degraded. Investigate and fix ASAP.")]

    def chaos_event_at(self, step: int) -> Optional[ChaosEvent]:
        return None

    def memory_hints(self) -> List[str]:
        return []

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self) -> Observation:
        self.step_count = 0
        self.done = False
        self.escalated = False
        self.patch_submitted = False
        self.escalation_hint_given = False
        self.agent_messages = []
        self._butterfly_triggered = False
        self._patch_content = None
        self._patch_description = None
        self._reset_time = time.time()
        self._chaos_events = []
        self._pr_review = None
        self._ci_status = None
        self._reasoning_log = []
        self._destructive_actions = 0
        self._collaboration_actions = 0
        self._restart_count = 0
        self._files = self.initial_files()
        self._log_buffer = list(self.initial_logs())
        self._jira_tickets = self.initial_jira_tickets()
        current_metrics = self.initial_metrics()
        self._metrics_history = [current_metrics]
        return self._build_observation(current_metrics, self.initial_alerts(), None, None)

    # ── Step ──────────────────────────────────────────────────────────────────

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, dict]:
        if self.done:
            raise RuntimeError("Episode done. Call reset().")

        self.step_count += 1
        action_result: Optional[str] = None
        action_error: Optional[str] = None

        # Track reasoning for explainability
        if action.reasoning:
            self._reasoning_log.append(f"step={self.step_count}: {action.reasoning}")

        # Safety check
        if action.action_type in (ActionType.ROLLBACK,):
            self._destructive_actions += 1
            self._log_buffer.append(f"[SAFETY] step={self.step_count}: Destructive action '{action.action_type}' executed by {action.agent}")

        # Collaboration tracking
        if action.action_type == ActionType.SEND_MESSAGE:
            self._collaboration_actions += 1

        try:
            action_result, action_error = self._execute_action(action)
        except Exception as exc:
            action_error = f"Internal error: {exc}"

        new_metrics = self.advance_metrics(self.step_count, action)
        self._metrics_history.append(new_metrics)
        self._check_butterfly(self.step_count, action)

        # Chaos injection
        chaos = self.chaos_event_at(self.step_count)
        if chaos:
            self._chaos_events.append(chaos)
            self._log_buffer.append(f"[CHAOS] {chaos.description}")

        reward = Reward(total=0.0, reason="Episode in progress")

        if self.patch_submitted:
            self.done = True
            reward = self.grade_patch(self._patch_content or "", self._patch_description or "")
            # Explainability bonus
            reward.explainability_score = min(1.0, len(self._reasoning_log) * 0.2)
            # Safety penalty
            reward.safety_score = max(0.0, 1.0 - self._destructive_actions * 0.3)
            # Collaboration bonus
            reward.collaboration_score = min(1.0, self._collaboration_actions * 0.25)
            # Apply escalation cap
            if self.escalated:
                reward.total = min(reward.total, 0.4)
                reward.escalation_penalty = -0.1
                reward.reason = f"[ESCALATED] {reward.reason}"
            # Apply safety penalty
            if self._destructive_actions > 0:
                reward.total = max(0.0, reward.total - self._destructive_actions * 0.1)
            # Recompute total with bonuses
            bonus = reward.explainability_score * 0.05 + reward.collaboration_score * 0.05
            reward.total = min(1.0, reward.total + bonus)

        elif self.step_count >= self.max_steps:
            self.done = True
            reward = Reward(total=0.05, reason="Max steps reached without patch.", steps_efficiency=0.0)

        obs = self._build_observation(new_metrics, self._current_alerts(), action_result, action_error)
        obs.done = self.done
        obs.chaos_events = list(self._chaos_events)

        info = {"step": self.step_count, "task_id": self.task_id,
                "butterfly_triggered": self._butterfly_triggered,
                "destructive_actions": self._destructive_actions}
        return obs, reward, self.done, info

    # ── Action execution ──────────────────────────────────────────────────────

    def _execute_action(self, action: Action) -> Tuple[Optional[str], Optional[str]]:
        t = action.action_type

        if t == ActionType.TERMINAL:
            return self._handle_terminal(action.command or ""), None

        elif t == ActionType.READ_FILE:
            path = action.file_path or ""
            if path in self._files:
                return self._files[path], None
            return None, f"File not found: {path}"

        elif t == ActionType.LIST_FILES:
            prefix = (action.file_path or "").rstrip("/")
            matches = [f for f in self._files if not prefix or f.startswith(prefix)]
            return "\n".join(sorted(matches)) or "(empty workspace)", None

        elif t == ActionType.EDIT_FILE:
            path = action.file_path or ""
            if not path:
                return None, "file_path required for EDIT_FILE"
            self._files[path] = action.content or ""
            self._log_buffer.append(f"[WORKSPACE] File edited: {path} ({len(action.content or '')} chars)")
            return f"✓ Written: {path}", None

        elif t == ActionType.SEARCH_LOGS:
            pattern = (action.command or "").lower()
            matches = [l for l in self._log_buffer if pattern in l.lower()]
            return ("\n".join(matches[-30:]) if matches else f"No matches for '{pattern}'"), None

        elif t == ActionType.SUBMIT_PATCH:
            self._patch_content = self._files.get(action.file_path or "", action.content or "")
            self._patch_description = action.patch_description or ""
            self.patch_submitted = True
            # Simulate CI/CD
            self._ci_status = "running"
            self._log_buffer.append(f"[CI/CD] Patch submitted for {action.file_path} — running tests...")
            # Create PR
            self._pr_review = PRReview(pr_id=f"PR-{self.step_count:03d}",
                                        status="pending",
                                        comments=["Automated review in progress..."])
            return "✓ Patch submitted. CI/CD pipeline triggered. PR created.", None

        elif t == ActionType.ESCALATE:
            if not self.escalated:
                self.escalated = True
                hint = self.escalation_hint()
                self._log_buffer.append("[ESCALATION] Human hint requested — max reward capped at 0.4")
                return f"[HUMAN HINT] {hint}\n\n⚠ Max reward capped at 0.4", None
            return "Already escalated.", None

        elif t == ActionType.SEND_MESSAGE:
            msg = AgentMessage(from_agent=action.agent,
                               to_agent=action.target_agent,
                               content=action.message or "",
                               step=self.step_count,
                               message_type="info")
            self.agent_messages.append(msg)
            self._log_buffer.append(f"[AGENT] {action.agent} → {action.target_agent or 'all'}: {(action.message or '')[:80]}")
            return f"Message sent to {action.target_agent or 'all agents'}", None

        elif t == ActionType.CREATE_JIRA:
            ticket = JiraTicket(id=f"INC-{len(self._jira_tickets)+1:03d}",
                                title=action.message or "Incident ticket",
                                description=action.patch_description or "",
                                status="open")
            self._jira_tickets.append(ticket)
            return f"✓ Jira ticket created: {ticket.id}", None

        elif t == ActionType.COMMENT_PR:
            if self._pr_review:
                self._pr_review.comments.append(action.message or "")
                return f"✓ Comment added to {self._pr_review.pr_id}", None
            return None, "No active PR to comment on"

        elif t == ActionType.RUN_TESTS:
            self._ci_status = "running"
            self._log_buffer.append(f"[CI/CD] Test suite triggered at step {self.step_count}")
            return "✓ Tests running... (results in next observation)", None

        elif t == ActionType.RESTART_SERVICE:
            self._restart_count += 1
            svc = action.service_name or "unknown"
            self._log_buffer.append(f"[OPS] Service '{svc}' restarted (restart #{self._restart_count})")
            self._check_butterfly(self.step_count, action)
            return f"✓ Service '{svc}' restarted. Note: this may be a band-aid fix.", None

        elif t == ActionType.ROLLBACK:
            self._destructive_actions += 1
            self._log_buffer.append(f"[ROLLBACK] Deployment rolled back at step {self.step_count} — DESTRUCTIVE ACTION")
            return "⚠ Rollback executed. Service may be unstable.", None

        return None, f"Unknown action: {t}"

    def _handle_terminal(self, command: str) -> str:
        cmd = command.strip()
        if cmd.startswith("grep"):
            parts = cmd.split()
            pattern = next((p.strip("'\"") for p in parts[1:] if not p.startswith("-")), "")
            matches = [l for l in self._log_buffer if pattern.lower() in l.lower()]
            return "\n".join(matches[-20:]) if matches else f"grep: no matches for '{pattern}'"
        if cmd.startswith("tail"):
            n = 20
            parts = cmd.split()
            for i, p in enumerate(parts):
                if p == "-n" and i + 1 < len(parts):
                    try: n = int(parts[i+1])
                    except: pass
            return "\n".join(self._log_buffer[-n:])
        if cmd in ("top", "htop", "ps aux"):
            m = self._metrics_history[-1]
            return (f"CPU: {m.cpu_percent:.1f}%  MEM: {m.memory_percent:.1f}%  "
                    f"LATENCY: {m.latency_ms:.0f}ms  ERR: {m.error_rate*100:.1f}%  "
                    f"CONNS: {m.active_connections}  DISK: {m.disk_io_mbps:.1f}MB/s")
        if cmd in ("cat /proc/meminfo", "free -m"):
            m = self._metrics_history[-1]
            used = int(m.memory_percent * 81.92)
            return f"MemTotal: 8192 MB\nMemUsed: {used} MB\nMemFree: {8192-used} MB"
        if cmd.startswith("ls"):
            path = cmd[2:].strip().strip("/")
            matches = [f for f in self._files if not path or f.startswith(path)]
            return "\n".join(sorted(matches)) or "(empty)"
        if cmd.startswith("cat "):
            path = cmd[4:].strip()
            return self._files.get(path, f"cat: {path}: No such file or directory")
        if cmd.startswith("diff "):
            return "[diff] File comparison not available in simulation"
        if cmd.startswith("git log"):
            return "[git] commit abc1234 — initial deployment\n[git] commit def5678 — hotfix attempt"
        if cmd.startswith("git diff"):
            return "[git] No staged changes"
        if cmd.startswith("curl") or cmd.startswith("wget"):
            return "[http] Simulated HTTP request — use read_file or search_logs for service data"
        if "npm test" in cmd or "pytest" in cmd or "jest" in cmd:
            self._ci_status = "running"
            return "[CI] Tests triggered — check ci_status in next observation"
        if "restart" in cmd or "systemctl" in cmd or "pm2" in cmd:
            self._restart_count += 1
            self._check_butterfly(self.step_count, None)
            return f"[OPS] Service restart #{self._restart_count} executed"
        return f"$ {cmd}\n[simulated] command executed."

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_observation(self, metrics, alerts, action_result, action_error) -> Observation:
        noise = self.NOISE_SCHEDULE.get(self.step_count, [])
        tp = "normal"
        if metrics.memory_percent > 85 or metrics.cpu_percent > 85 or metrics.error_rate > 0.5:
            tp = "elevated"
        if metrics.memory_percent > 95 or metrics.cpu_percent > 95 or metrics.error_rate > 0.8:
            tp = "critical"

        # Update CI status
        if self._ci_status == "running" and self.step_count > 1:
            self._ci_status = "passing" if self.patch_submitted else "failing"

        return Observation(
            step=self.step_count, task_id=self.task_id, metrics=metrics,
            active_alerts=alerts, recent_logs=list(self._log_buffer[-30:]),
            agent_messages=list(self.agent_messages[-10:]),
            noise_events=noise, action_result=action_result, action_error=action_error,
            available_files=sorted(self._files.keys()),
            escalated=self.escalated,
            escalation_hint=self.escalation_hint() if self.escalated else None,
            done=self.done, time_pressure=tp,
            jira_tickets=list(self._jira_tickets),
            pr_review=self._pr_review,
            chaos_events=list(self._chaos_events[-3:]),
            memory_hints=self.memory_hints(),
            difficulty_level=self._difficulty,
            ci_status=self._ci_status,
        )

    def _current_alerts(self) -> List[Alert]:
        return self.initial_alerts()

    def _check_butterfly(self, step: int, action: Optional[Action]) -> None:
        pass

    def state(self) -> dict:
        m = self._metrics_history[-1] if self._metrics_history else self.initial_metrics()
        return {
            "task_id": self.task_id, "step": self.step_count, "max_steps": self.max_steps,
            "done": self.done, "escalated": self.escalated, "patch_submitted": self.patch_submitted,
            "current_metrics": m.model_dump(), "butterfly_triggered": self._butterfly_triggered,
            "difficulty": self._difficulty, "restart_count": self._restart_count,
            "destructive_actions": self._destructive_actions,
            "collaboration_actions": self._collaboration_actions,
            "ci_status": self._ci_status,
        }
