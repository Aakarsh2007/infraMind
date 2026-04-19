"""
InfraMind — Baseline Inference Script
OpenEnv Hackathon Round 1 — Strictly compliant with sample inference.py format.

STDOUT FORMAT (exact — no deviation allowed):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

Mandatory env vars (per hackathon spec):
  API_BASE_URL   — The API endpoint for the LLM
  MODEL_NAME     — The model identifier to use for inference
  HF_TOKEN       — Your Hugging Face / API key
  OPENAI_API_KEY — OpenAI API key (alternative to HF_TOKEN)

Optional:
  INFRA_ENV_URL  — InfraMind environment URL (default: http://localhost:7860)
  INFERENCE_SEED — Reproducibility seed (default: 42)
  FULL_RUN       — Set to "1" to run all 5 tasks (default: 3 required tasks)
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import httpx
from openai import OpenAI

# ── Mandatory env vars (per hackathon spec) ───────────────────────────────────
# API_BASE_URL = LLM endpoint (as required by hackathon)
# Defaults set ONLY for API_BASE_URL and MODEL_NAME (not HF_TOKEN)
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
MODEL_NAME   = os.getenv("MODEL_NAME") or "gpt-4o-mini"
HF_TOKEN     = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

# InfraMind environment URL (separate from LLM endpoint)
INFRA_ENV_URL = os.getenv("INFRA_ENV_URL") or "http://localhost:7860"

INFERENCE_SEED = int(os.getenv("INFERENCE_SEED") or "42")
BENCHMARK = "infra-mind"

# 3 required tasks for baseline; FULL_RUN=1 runs all 6
TASK_IDS: List[str] = (
    ["memory_leak", "db_deadlock", "cascade_failure", "cpu_spike", "auth_bypass", "k8s_cluster_compromise"]
    if os.getenv("FULL_RUN") == "1"
    else ["memory_leak", "db_deadlock", "cascade_failure"]
)
MAX_STEPS_PER_TASK = 50  # supports super long-horizon tasks
SUCCESS_SCORE_THRESHOLD = 0.3

# ── OpenAI client — uses API_BASE_URL as LLM endpoint (per hackathon spec) ───
API_KEY = HF_TOKEN or os.getenv("OPENAI_API_KEY") or "no-key"
openai_client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# InfraMind environment HTTP client
http = httpx.Client(base_url=INFRA_ENV_URL, timeout=60.0)

# Global timeout guard — 18 min hard cap (< 20 min requirement)
INFERENCE_START = time.time()
MAX_TOTAL_SECONDS = 18 * 60

# ── Mandatory log helpers — exact format, no deviation ───────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    action_clean = action.replace("\n", " ").replace('"', "'")[:80]
    print(
        f"[STEP] step={step} action={action_clean} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )

# ── Environment helpers ───────────────────────────────────────────────────────

def env_reset(task_id: str) -> Dict[str, Any]:
    r = http.post("/reset", json={"task_id": task_id, "model": MODEL_NAME, "seed": INFERENCE_SEED})
    r.raise_for_status()
    return r.json()

def env_step(action: Dict[str, Any]) -> Dict[str, Any]:
    r = http.post("/step", json=action)
    r.raise_for_status()
    return r.json()

# ── Agent system prompt ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an elite SRE AI agent in the InfraMind environment.
Your goal: diagnose and fix the production incident.

STRATEGY:
1. list_files — see the workspace
2. search_logs ERROR — find the problem
3. read_file <suspicious_file> — understand the bug
4. edit_file <file> with the complete fixed code
5. submit_patch with a clear patch_description

Respond ONLY with a JSON object (no markdown):
{
  "agent": "debugger|coder|coordinator",
  "action_type": "terminal|read_file|edit_file|list_files|search_logs|submit_patch",
  "command": "...",
  "file_path": "...",
  "content": "...",
  "patch_description": "..."
}

Rules: submit_patch ends the episode. Do NOT escalate. Be efficient."""

def _obs_to_prompt(obs: Dict[str, Any]) -> str:
    m = obs.get("metrics", {})
    parts = [
        f"STEP={obs.get('step', 0)} TASK={obs.get('task_id')} PRESSURE={obs.get('time_pressure', 'normal')}",
        f"CPU={m.get('cpu_percent')}% MEM={m.get('memory_percent')}% ERR={m.get('error_rate', 0)*100:.1f}%",
    ]
    alerts = obs.get("active_alerts", [])
    if alerts:
        parts.append("ALERTS: " + " | ".join(
            f"[{a['severity'].upper()}] {a['service']}: {a['message']}" for a in alerts[:2]
        ))
    logs = obs.get("recent_logs", [])
    if logs:
        parts.append("LOGS:\n" + "\n".join(logs[-8:]))
    files = obs.get("available_files", [])
    if files:
        parts.append("FILES: " + ", ".join(files))
    if obs.get("action_result"):
        parts.append("RESULT:\n" + str(obs["action_result"])[:800])
    if obs.get("action_error"):
        parts.append("ERROR: " + str(obs["action_error"]))
    return "\n".join(parts)

def get_agent_action(history: List[Dict], obs: Dict[str, Any]) -> Dict[str, Any]:
    history.append({"role": "user", "content": _obs_to_prompt(obs)})
    response = openai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history[-14:],
        temperature=0.1,
        max_tokens=500,
    )
    raw = (response.choices[0].message.content or "{}").strip()
    history.append({"role": "assistant", "content": raw})
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
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    last_error: Optional[str] = None

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = env_reset(task_id)
        history: List[Dict] = []
        done = False

        for step in range(1, MAX_STEPS_PER_TASK + 1):
            # Global timeout guard
            if time.time() - INFERENCE_START > MAX_TOTAL_SECONDS:
                log_step(step=step, action="timeout_guard", reward=0.0, done=False, error="global_timeout")
                break

            if done:
                break

            try:
                action_dict = get_agent_action(history, obs)
            except Exception as e:
                action_dict = {"agent": "debugger", "action_type": "search_logs", "command": "ERROR"}
                last_error = str(e)

            action_str = action_dict.get("action_type", "unknown")

            try:
                result = env_step(action_dict)
            except Exception as e:
                last_error = str(e)
                log_step(step=step, action=action_str, reward=0.0, done=False, error=last_error)
                break

            obs = result.get("observation", {})
            reward_data = result.get("reward", {})
            done = result.get("done", False)
            step_reward = float(reward_data.get("total", 0.0)) if done else 0.0
            last_error = obs.get("action_error") or None

            rewards.append(step_reward)
            steps_taken = step

            log_step(step=step, action=action_str, reward=step_reward, done=done, error=last_error)

            if done:
                score = float(reward_data.get("total", 0.0))
                break

        # Force submit if not done (always emit [END])
        if not done:
            try:
                files = obs.get("available_files", [])
                result = env_step({
                    "agent": "coder",
                    "action_type": "submit_patch",
                    "file_path": files[0] if files else "",
                    "patch_description": "Timeout — best-effort patch",
                })
                reward_data = result.get("reward", {})
                score = float(reward_data.get("total", 0.0))
                rewards.append(score)
                steps_taken += 1
                log_step(step=steps_taken, action="submit_patch", reward=score, done=True, error=None)
            except Exception as e:
                score = 0.0
                last_error = str(e)

        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        last_error = str(e)
        score = 0.0
        success = False

    # Always emit [END] — even on exception (per spec)
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return {"task_id": task_id, "score": score, "steps": steps_taken, "success": success, "rewards": rewards}

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"InfraMind | LLM={API_BASE_URL} | MODEL={MODEL_NAME} | ENV={INFRA_ENV_URL} | SEED={INFERENCE_SEED}", flush=True)

    # Verify InfraMind environment is reachable
    try:
        r = http.get("/health")
        r.raise_for_status()
        print(f"Environment health: {r.json().get('status')} — OK", flush=True)
    except Exception as e:
        print(f"ERROR: Cannot reach InfraMind at {INFRA_ENV_URL}: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for task_id in TASK_IDS:
        try:
            result = run_task(task_id)
            results.append(result)
        except Exception as e:
            print(f"ERROR running {task_id}: {e}", file=sys.stderr)
            # Always emit [END] even on exception
            log_end(success=False, steps=0, score=0.0, rewards=[])
            results.append({"task_id": task_id, "score": 0.0, "steps": 0, "success": False, "rewards": []})

    avg_score = sum(r["score"] for r in results) / max(len(results), 1)
    print(f"\n{'='*55}", flush=True)
    print(f"INFRA MIND BASELINE — Model: {MODEL_NAME}", flush=True)
    for r in results:
        grade = "S" if r["score"] >= 0.9 else "A" if r["score"] >= 0.7 else "B" if r["score"] >= 0.5 else "C" if r["score"] >= 0.3 else "F"
        print(f"  {'✓' if r['success'] else '✗'} {r['task_id']:22s}  score={r['score']:.2f}  steps={r['steps']}  grade={grade}", flush=True)
    print(f"  {'AVERAGE':24s}  score={avg_score:.2f}", flush=True)
    print(f"{'='*55}", flush=True)


if __name__ == "__main__":
    main()
