"""
InfraMind Baseline Inference Script
OpenEnv Hackathon — Round 1 compliant.

Mandatory format:
  [START] {"task_id": "...", "model": "..."}
  [STEP]  {"step": N, "action": "...", "observation": "...", "reward": R, "done": false}
  [END]   {"task_id": "...", "reward": R, "steps": N, "status": "success"}

Reads: API_BASE_URL, MODEL_NAME, HF_TOKEN, OPENAI_API_KEY from environment.
Uses: OpenAI client for all LLM calls.
Runtime: < 20 min on 2vCPU / 8GB RAM.
Reproducible: set INFERENCE_SEED env var for deterministic runs.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import httpx
from openai import OpenAI

# ── Mandatory env vars ────────────────────────────────────────────────────────
API_BASE_URL   = os.environ.get("API_BASE_URL", "http://localhost:7860")
MODEL_NAME     = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN       = os.environ.get("HF_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Run only the 3 required tasks for baseline (keeps runtime < 5 min)
# Full 5-task run available via FULL_RUN=1 env var
TASK_IDS: List[str] = (
    ["memory_leak", "db_deadlock", "cascade_failure", "cpu_spike", "auth_bypass"]
    if os.environ.get("FULL_RUN") == "1"
    else ["memory_leak", "db_deadlock", "cascade_failure"]
)
MAX_STEPS_PER_TASK = 25
INFERENCE_SEED = int(os.environ.get("INFERENCE_SEED", "42"))  # Reproducible seed

# ── Clients ───────────────────────────────────────────────────────────────────
openai_client = OpenAI(
    api_key=OPENAI_API_KEY or HF_TOKEN or "no-key",
)
http = httpx.Client(base_url=API_BASE_URL, timeout=60.0)

# Timeout guard — ensures inference never runs > 18 min total
INFERENCE_START = time.time()
MAX_TOTAL_SECONDS = 18 * 60  # 18 min hard cap (leaves 2 min buffer)

# ── Environment helpers ───────────────────────────────────────────────────────
def env_reset(task_id: str) -> Dict[str, Any]:
    r = http.post("/reset", json={"task_id": task_id, "model": MODEL_NAME, "seed": INFERENCE_SEED})
    r.raise_for_status()
    return r.json()

def env_step(action: Dict[str, Any]) -> Dict[str, Any]:
    r = http.post("/step", json=action)
    r.raise_for_status()
    return r.json()

def env_state() -> Dict[str, Any]:
    r = http.get("/state")
    r.raise_for_status()
    return r.json()

# ── Agent ─────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are an elite SRE AI agent in the Gravex-Aegis War-Room environment.
You coordinate: coordinator, debugger, coder, reviewer, sre agents.

STRATEGY (follow this order):
1. list_files to see the workspace
2. search_logs with "ERROR" to find the problem
3. read_file on the suspicious file
4. edit_file with the complete fixed code
5. submit_patch with a clear patch_description

Respond ONLY with a JSON object (no markdown, no explanation):
{
  "agent": "debugger|coder|coordinator|reviewer|sre",
  "action_type": "terminal|read_file|edit_file|list_files|search_logs|submit_patch|escalate",
  "command": "...",
  "file_path": "...",
  "content": "...",
  "patch_description": "..."
}

Rules:
- submit_patch ends the episode and triggers grading
- Do NOT escalate (caps reward at 0.4)
- Be efficient — fewer steps = higher reward bonus
"""

def _obs_summary(obs: Dict[str, Any]) -> str:
    m = obs.get("metrics", {})
    parts = [
        f"STEP={obs.get('step',0)} TASK={obs.get('task_id')} PRESSURE={obs.get('time_pressure','normal')}",
        f"CPU={m.get('cpu_percent')}% MEM={m.get('memory_percent')}% ERR={m.get('error_rate',0)*100:.1f}%",
    ]
    alerts = obs.get("active_alerts", [])
    if alerts:
        parts.append("ALERTS: " + " | ".join(f"[{a['severity'].upper()}] {a['service']}: {a['message']}" for a in alerts[:3]))
    logs = obs.get("recent_logs", [])
    if logs:
        parts.append("LOGS:\n" + "\n".join(logs[-10:]))
    files = obs.get("available_files", [])
    if files:
        parts.append("FILES: " + ", ".join(files))
    if obs.get("action_result"):
        parts.append("RESULT:\n" + str(obs["action_result"])[:1000])
    if obs.get("action_error"):
        parts.append("ERROR: " + str(obs["action_error"]))
    return "\n".join(parts)

def get_agent_action(history: List[Dict], obs: Dict[str, Any]) -> Dict[str, Any]:
    history.append({"role": "user", "content": _obs_summary(obs)})
    response = openai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history[-16:],
        temperature=0.1,
        max_tokens=600,
    )
    raw = (response.choices[0].message.content or "{}").strip()
    history.append({"role": "assistant", "content": raw})
    # Strip markdown fences
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"agent": "debugger", "action_type": "search_logs", "command": "ERROR"}

# ── Run one task episode ──────────────────────────────────────────────────────
def run_task(task_id: str) -> Dict[str, Any]:
    # ── [START] log — exact required format ──────────────────────────────────
    print(json.dumps({"type": "START", "task_id": task_id, "model": MODEL_NAME}), flush=True)
    print(f'[START] {{"task_id": "{task_id}", "model": "{MODEL_NAME}"}}', flush=True)

    obs = env_reset(task_id)
    history: List[Dict] = []
    done = False
    step = 0
    total_reward = 0.0
    final_reward: Optional[Dict] = None
    episode_start = time.time()

    while not done and step < MAX_STEPS_PER_TASK:
        # Global timeout guard
        if time.time() - INFERENCE_START > MAX_TOTAL_SECONDS:
            print(f'[STEP] {{"step": {step}, "action": "timeout_guard", "observation": "global_timeout", "reward": null, "done": false}}', flush=True)
            break
        step += 1
        t0 = time.time()

        # Get action from LLM
        try:
            action = get_agent_action(history, obs)
        except Exception as e:
            action = {"agent": "debugger", "action_type": "search_logs", "command": "ERROR"}

        # Execute in environment
        try:
            result = env_step(action)
        except Exception as e:
            # ── [STEP] log ────────────────────────────────────────────────────
            print(f'[STEP] {{"step": {step}, "action": "{action.get("action_type","unknown")}", "observation": "env_error", "reward": null, "done": false}}', flush=True)
            break

        obs = result.get("observation", {})
        reward_data = result.get("reward", {})
        done = result.get("done", False)

        if done:
            final_reward = reward_data
            total_reward = reward_data.get("total", 0.0)

        elapsed = round(time.time() - t0, 3)

        # ── [STEP] log — exact required format ───────────────────────────────
        obs_summary = f"step={obs.get('step')} cpu={obs.get('metrics',{}).get('cpu_percent')}% done={done}"
        print(
            f'[STEP] {{"step": {step}, "action": "{action.get("action_type","unknown")}", "observation": "{obs_summary}", "reward": {total_reward if done else "null"}, "done": {str(done).lower()}}}',
            flush=True,
        )

    # If not done by max steps, force submit
    if not done:
        try:
            files = obs.get("available_files", [])
            target = files[0] if files else ""
            result = env_step({
                "agent": "coder",
                "action_type": "submit_patch",
                "file_path": target,
                "patch_description": "Timeout — submitting best-effort patch after max steps",
            })
            final_reward = result.get("reward", {})
            total_reward = final_reward.get("total", 0.0)
            done = True
        except Exception:
            total_reward = 0.0
            final_reward = {"total": 0.0, "reason": "timeout"}

    duration = round(time.time() - episode_start, 2)
    status = "success" if total_reward > 0 else "failed"

    # ── [END] log — exact required format ────────────────────────────────────
    print(
        f'[END] {{"task_id": "{task_id}", "reward": {total_reward}, "steps": {step}, "status": "{status}"}}',
        flush=True,
    )

    return {
        "task_id": task_id,
        "total_reward": total_reward,
        "steps": step,
        "duration_s": duration,
        "final_reward": final_reward,
    }

# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print(f"InfraMind Baseline Inference", flush=True)
    print(f"API_BASE_URL={API_BASE_URL}  MODEL={MODEL_NAME}  SEED={INFERENCE_SEED}  TASKS={TASK_IDS}", flush=True)

    # Verify environment is reachable
    try:
        r = http.get("/health")
        r.raise_for_status()
        print(f"Environment health: {r.json()}", flush=True)
    except Exception as e:
        print(f"ERROR: Cannot reach environment at {API_BASE_URL}: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for task_id in TASK_IDS:
        try:
            result = run_task(task_id)
            results.append(result)
        except Exception as e:
            print(f"ERROR running task {task_id}: {e}", file=sys.stderr)
            results.append({"task_id": task_id, "total_reward": 0.0, "steps": 0, "duration_s": 0})

    # Summary
    avg_reward = sum(r["total_reward"] for r in results) / max(len(results), 1)
    print(f"\n{'='*60}", flush=True)
    print(f"BASELINE RESULTS — Model: {MODEL_NAME}", flush=True)
    for r in results:
        grade = "S" if r["total_reward"] >= 0.9 else "A" if r["total_reward"] >= 0.7 else "B" if r["total_reward"] >= 0.5 else "C" if r["total_reward"] >= 0.3 else "F"
        print(f"  {r['task_id']:25s}  reward={r['total_reward']:.3f}  steps={r['steps']}  grade={grade}", flush=True)
    print(f"  {'AVERAGE':25s}  reward={avg_reward:.3f}", flush=True)
    print(f"{'='*60}", flush=True)


if __name__ == "__main__":
    main()
