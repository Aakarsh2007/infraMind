"""
AegisSwarmEnv — Complete engine.
Gravex-Aegis: Autonomous DevOps War-Room Environment
Features: 5 tasks, leaderboard, run history, feedback loop,
agent memory, dynamic difficulty, custom scenarios, stats.
"""
from __future__ import annotations
import threading, time, uuid, json
from typing import Any, Dict, List, Optional, Tuple
from env.models import Action, FeedbackRequest, CustomScenarioRequest, Observation, Reward
from env.scenarios import SCENARIOS
from env.scenarios.base import BaseScenario

TASK_META = [
    {"id": "memory_leak",    "name": "Task 1 — Memory Leak",              "difficulty": "easy",        "max_steps": 20, "description": "Fix an unbounded cache causing OOM in a Node.js API.", "tags": ["nodejs","cache","memory"]},
    {"id": "db_deadlock",    "name": "Task 2 — Database Deadlock",         "difficulty": "medium",      "max_steps": 30, "description": "Fix inconsistent lock ordering causing PostgreSQL deadlocks.", "tags": ["postgres","concurrency","transactions"]},
    {"id": "cascade_failure","name": "Task 3 — Distributed Cascade",       "difficulty": "hard",        "max_steps": 40, "description": "Find the Redis timeout root cause behind a 3-service cascade failure.", "tags": ["redis","microservices","cascade"]},
    {"id": "cpu_spike",      "name": "Task 4 — CPU Spike / Infinite Loop", "difficulty": "medium-hard", "max_steps": 25, "description": "Fix a recursive sanitizer with no depth limit causing 100% CPU.", "tags": ["nodejs","recursion","cpu"]},
    {"id": "auth_bypass",    "name": "Task 5 — Auth Bypass (Security)",    "difficulty": "hard",        "max_steps": 30, "description": "Patch a JWT 'none' algorithm vulnerability before the breach escalates.", "tags": ["security","jwt","auth"]},
]


class FeedbackRecord:
    def __init__(self, run_id: str, task_id: str, rating: str, comment: str,
                 correct_fix: str, suggested_improvement: str):
        self.run_id = run_id
        self.task_id = task_id
        self.rating = rating
        self.comment = comment
        self.correct_fix = correct_fix
        self.suggested_improvement = suggested_improvement
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {"run_id": self.run_id, "task_id": self.task_id, "rating": self.rating,
                "comment": self.comment, "timestamp": self.timestamp}


class RunRecord:
    def __init__(self, run_id, task_id, model, reward, steps, escalated,
                 butterfly, post_mortem, duration_s, difficulty):
        self.run_id = run_id; self.task_id = task_id; self.model = model
        self.reward = reward; self.steps = steps; self.escalated = escalated
        self.butterfly = butterfly; self.post_mortem = post_mortem
        self.duration_s = duration_s; self.difficulty = difficulty
        self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {"run_id": self.run_id, "task_id": self.task_id, "model": self.model,
                "reward": self.reward, "steps": self.steps, "escalated": self.escalated,
                "butterfly_triggered": self.butterfly, "duration_s": round(self.duration_s, 2),
                "difficulty": self.difficulty, "timestamp": self.timestamp,
                "post_mortem": self.post_mortem}


class AgentMemory:
    """Persists knowledge across episodes — agents remember past incidents."""
    def __init__(self):
        self._memory: List[Dict] = []
        self._lock = threading.RLock()

    def record(self, task_id: str, root_cause: str, fix_summary: str, reward: float):
        with self._lock:
            self._memory.append({"task_id": task_id, "root_cause": root_cause,
                                  "fix_summary": fix_summary, "reward": reward,
                                  "timestamp": time.time()})
            if len(self._memory) > 100:
                self._memory = self._memory[-100:]

    def hints_for(self, task_id: str) -> List[str]:
        with self._lock:
            relevant = [m for m in self._memory if m["task_id"] == task_id and m["reward"] > 0.5]
            if not relevant:
                return []
            best = sorted(relevant, key=lambda x: -x["reward"])[:2]
            return [f"Memory: Previous fix for {m['task_id']}: {m['fix_summary']} (reward={m['reward']:.2f})"
                    for m in best]

    def all(self) -> List[dict]:
        with self._lock:
            return list(reversed(self._memory))


class DifficultyAdapter:
    """Adjusts difficulty based on agent performance history."""
    def __init__(self):
        self._history: Dict[str, List[float]] = {}
        self._lock = threading.RLock()

    def record(self, task_id: str, reward: float):
        with self._lock:
            self._history.setdefault(task_id, []).append(reward)
            if len(self._history[task_id]) > 10:
                self._history[task_id] = self._history[task_id][-10:]

    def difficulty_for(self, task_id: str) -> float:
        with self._lock:
            history = self._history.get(task_id, [])
            if len(history) < 3:
                return 1.0
            avg = sum(history[-3:]) / 3
            if avg > 0.8:
                return min(2.0, 1.0 + (avg - 0.8) * 5)  # Too easy → harder
            elif avg < 0.3:
                return max(0.5, 1.0 - (0.3 - avg) * 2)  # Too hard → easier
            return 1.0

    def all_difficulties(self) -> Dict[str, float]:
        with self._lock:
            return {tid: self.difficulty_for(tid) for tid in self._history}


class AegisSwarmEnv:
    TASK_IDS = [t["id"] for t in TASK_META]

    def __init__(self):
        self._lock = threading.RLock()  # Reentrant — safe for nested calls
        self._scenario: Optional[BaseScenario] = None
        self._last_obs: Optional[Observation] = None
        self._run_history: List[RunRecord] = []
        self._feedback_history: List[FeedbackRecord] = []
        self._current_run_id: Optional[str] = None
        self._current_model: str = "unknown"
        self._episode_start: float = 0.0
        self._memory = AgentMemory()
        self._difficulty_adapter = DifficultyAdapter()
        self._custom_scenarios: Dict[str, Any] = {}

    # ── OpenEnv interface ─────────────────────────────────────────────────────

    def reset(self, task_id: Optional[str] = None, model: str = "unknown") -> Observation:
        with self._lock:
            tid = task_id or "memory_leak"
            if tid not in SCENARIOS and tid not in self._custom_scenarios:
                raise ValueError(f"Unknown task_id '{tid}'. Valid: {list(SCENARIOS.keys()) + list(self._custom_scenarios.keys())}")
            difficulty = self._difficulty_adapter.difficulty_for(tid)
            if tid in self._custom_scenarios:
                from env.scenarios.custom import CustomScenario
                self._scenario = CustomScenario(self._custom_scenarios[tid], difficulty)
            else:
                self._scenario = SCENARIOS[tid](difficulty)
            # Inject memory hints
            hints = self._memory.hints_for(tid)
            self._scenario._memory_hints_override = hints
            self._current_run_id = str(uuid.uuid4())[:8]
            self._current_model = model
            self._episode_start = time.time()
            obs = self._scenario.reset()
            obs.memory_hints = hints
            self._last_obs = obs
            return obs

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        with self._lock:
            if self._scenario is None:
                raise RuntimeError("Call reset() before step()")
            obs, reward, done, info = self._scenario.step(action)
            self._last_obs = obs
            if done:
                self._record_run(reward, info)
                if reward.post_mortem:
                    self._memory.record(
                        self._scenario.task_id,
                        str(reward.post_mortem.get("root_cause", "")),
                        str(reward.post_mortem.get("optimal_fix", reward.reason)),
                        reward.total,
                    )
                self._difficulty_adapter.record(self._scenario.task_id, reward.total)
            return obs, reward, done, info

    def state(self) -> Dict[str, Any]:
        with self._lock:
            if self._scenario is None:
                return {"status": "not_started", "message": "Call reset() to begin."}
            s = self._scenario.state()
            s.update({"run_id": self._current_run_id, "model": self._current_model,
                       "elapsed_s": round(time.time() - self._episode_start, 1)})
            return s

    def tasks(self) -> list:
        tasks = list(TASK_META)
        for name, cfg in self._custom_scenarios.items():
            tasks.append({"id": name, "name": cfg["name"], "difficulty": cfg["difficulty"],
                          "max_steps": 25, "description": cfg["description"], "tags": ["custom"]})
        return tasks

    # ── Extended features ─────────────────────────────────────────────────────

    def submit_feedback(self, feedback: FeedbackRequest) -> dict:
        rec = FeedbackRecord(feedback.run_id, "", feedback.rating,
                             feedback.comment or "", feedback.correct_fix or "",
                             feedback.suggested_improvement or "")
        # Find matching run
        for run in self._run_history:
            if run.run_id == feedback.run_id:
                rec.task_id = run.task_id
                break
        self._feedback_history.append(rec)
        return {"status": "recorded", "run_id": feedback.run_id,
                "message": "Thank you! Your feedback helps improve the environment."}

    def leaderboard(self) -> List[dict]:
        with self._lock:
            runs = sorted(self._run_history, key=lambda r: (-r.reward, r.steps))
            return [r.to_dict() for r in runs[:20]]

    def history(self) -> List[dict]:
        with self._lock:
            return [r.to_dict() for r in reversed(self._run_history)]

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            if not self._run_history:
                return {"total_runs": 0, "message": "No runs yet. Start an episode!"}
            by_task: Dict[str, List[float]] = {}
            for r in self._run_history:
                by_task.setdefault(r.task_id, []).append(r.reward)
            return {
                "total_runs": len(self._run_history),
                "avg_reward": round(sum(r.reward for r in self._run_history) / len(self._run_history), 3),
                "best_reward": round(max(r.reward for r in self._run_history), 3),
                "total_feedback": len(self._feedback_history),
                "by_task": {tid: {"runs": len(v), "avg": round(sum(v)/len(v), 3), "best": round(max(v), 3)}
                            for tid, v in by_task.items()},
                "dynamic_difficulties": self._difficulty_adapter.all_difficulties(),
            }

    def memory(self) -> List[dict]:
        return self._memory.all()

    def feedback_summary(self) -> dict:
        if not self._feedback_history:
            return {"total": 0}
        ratings = [f.rating for f in self._feedback_history]
        return {
            "total": len(ratings),
            "thumbs_up": ratings.count("thumbs_up"),
            "thumbs_down": ratings.count("thumbs_down"),
            "neutral": ratings.count("neutral"),
            "recent": [f.to_dict() for f in self._feedback_history[-5:]],
        }

    def add_custom_scenario(self, req: CustomScenarioRequest) -> dict:
        sid = req.name.lower().replace(" ", "_")
        self._custom_scenarios[sid] = req.model_dump()
        return {"status": "created", "task_id": sid, "message": f"Custom scenario '{req.name}' added."}

    def _record_run(self, reward: Reward, info: dict):
        if not self._scenario or not self._current_run_id:
            return
        rec = RunRecord(
            run_id=self._current_run_id, task_id=self._scenario.task_id,
            model=self._current_model, reward=reward.total,
            steps=self._scenario.step_count, escalated=self._scenario.escalated,
            butterfly=self._scenario._butterfly_triggered,
            post_mortem=reward.post_mortem,
            duration_s=time.time() - self._episode_start,
            difficulty=self._scenario._difficulty,
        )
        self._run_history.append(rec)


_env_instance: Optional[AegisSwarmEnv] = None
_env_lock = threading.Lock()

def get_env() -> AegisSwarmEnv:
    global _env_instance
    with _env_lock:
        if _env_instance is None:
            _env_instance = AegisSwarmEnv()
        return _env_instance
