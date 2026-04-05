"""Quick verification script — run with: python verify.py"""
import sys
sys.path.insert(0, '.')

from env.engine import get_env
from env.models import Action, ActionType, AgentRole, FeedbackRequest

env = get_env()

print("Testing all 5 tasks...")
for tid in ['memory_leak', 'db_deadlock', 'cascade_failure', 'cpu_spike', 'auth_bypass']:
    obs = env.reset(tid, model='test')
    assert obs.task_id == tid and obs.step == 0

    a = Action(agent=AgentRole.DEBUGGER, action_type=ActionType.SEARCH_LOGS, command='ERROR')
    obs2, rew, done, info = env.step(a)
    assert not done

    a2 = Action(
        agent=AgentRole.CODER,
        action_type=ActionType.SUBMIT_PATCH,
        file_path=obs2.available_files[0],
        patch_description='Fixed root cause',
        reasoning='test'
    )
    obs3, rew2, done2, info2 = env.step(a2)
    assert done2
    assert 0.0 <= rew2.total <= 1.0
    print(f"  {tid}: reward={rew2.total:.3f}  tests={rew2.hidden_tests_passed:.2f}  OK")

print("\nTesting feedback...")
fb = FeedbackRequest(run_id='test', rating='thumbs_up', comment='Great fix')
result = env.submit_feedback(fb)
assert result['status'] == 'recorded'
print("  feedback: OK")

print("\nTesting leaderboard + stats...")
lb = env.leaderboard()
st = env.stats()
assert st['total_runs'] == 5
assert len(lb) == 5
print(f"  leaderboard: {len(lb)} entries")
print(f"  stats: avg={st['avg_reward']:.3f}  best={st['best_reward']:.3f}")

print("\nTesting memory...")
mem = env.memory()
assert len(mem) > 0
print(f"  memory: {len(mem)} entries")

print("\nTesting dynamic difficulty...")
difficulties = st.get('dynamic_difficulties', {})
print(f"  difficulties: {difficulties}")

print("\nALL CHECKS PASSED")
