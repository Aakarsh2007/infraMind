"""Test judge mode, trace export, seeded reproducibility."""
import sys
sys.path.insert(0, '.')
from env.engine import get_env
from env.models import Action, ActionType, AgentRole

env = get_env()

print("Testing judge mode...")
result = env.judge_run_all(seed=42)
assert "avg_score" in result
assert "tasks" in result
assert "diagnostics" in result
assert len(result["tasks"]) == 5
print(f"  judge avg_score={result['avg_score']:.3f}")
print(f"  diagnostics={result['diagnostics']}")

print("\nTesting seeded reproducibility...")
obs1 = env.reset("memory_leak", seed=1234)
obs2 = env.reset("memory_leak", seed=1234)
assert obs1.seed == obs2.seed == 1234
assert obs1.available_files == obs2.available_files
print(f"  seed=1234 → same files: {obs1.available_files[:2]}")

print("\nTesting episode trace export...")
obs = env.reset("memory_leak", model="test", seed=99)
a = Action(agent=AgentRole.DEBUGGER, action_type=ActionType.SEARCH_LOGS, command="ERROR", reasoning="finding errors")
env.step(a)
a2 = Action(agent=AgentRole.CODER, action_type=ActionType.SUBMIT_PATCH,
            file_path=obs.available_files[0], patch_description="fixed the cache leak")
_, rew, done, info = env.step(a2)
assert done
run_id = env._current_run_id
trace = env.export_trace(run_id)
assert trace is not None
assert trace.seed == 99
assert len(trace.steps) >= 2
assert trace.final_reward > 0
print(f"  trace run_id={run_id} steps={len(trace.steps)} reward={trace.final_reward:.3f}")

print("\nTesting skill breakdown...")
assert rew.skill_breakdown is not None
print(f"  root_cause_accuracy={rew.skill_breakdown.root_cause_accuracy:.2f}")
print(f"  patch_quality={rew.skill_breakdown.patch_quality:.2f}")
print(f"  noise_filtering={rew.skill_breakdown.noise_filtering:.2f}")

print("\nTesting failure report...")
assert rew.failure_report is not None
print(f"  verdict={rew.failure_report.final_verdict}")
print(f"  root_cause={rew.failure_report.root_cause}")

print("\nTesting feedback learning...")
from env.models import FeedbackRequest
fb = FeedbackRequest(run_id=run_id, rating="thumbs_down", comment="agent missed root cause")
result = env.submit_feedback(fb)
assert result["learning_applied"] == True
print(f"  learning_applied={result['learning_applied']}")
print(f"  adjustments={result['adjustments']}")

print("\nALL JUDGE/TRACE/SEED CHECKS PASSED")
