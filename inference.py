"""
InfraMind — Baseline Inference Script
OpenEnv Hackathon Round 1 — Fully compliant with mandatory stdout format.

STDOUT FORMAT (exact — no deviation):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

Env vars:
  API_BASE_URL   — environment API endpoint
  MODEL_NAME     — model identifier
  HF_TOKEN       — Hugging Face / API key
  OPENAI_API_KEY — OpenAI API key
  INFERENCE_SEED — seed for reproducibility (default: 42)
  FULL_RUN       — set to "1" to run all 5 tasks (default: 3 required tasks)
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
INFERENCE_SEED = int(os.environ.get("INFERENCE_SEED", "42"))

BENCHMARK = "infra-mind"

# 3 required tasks for baseline; FULL_RUN=1 runs all 5
TASK_IDS: List[str] = (
    ["memory_leak", "db_deadlock", "cascade_failure", "cpu_spike", "auth_bypass"]
    if os.environ.get("FULL_RUN") == "1"
    else ["memory_leak", "db_deadlock", "cascade_failure"]
)
MAX_STEPS_PER_TASK = 20  # keeps runtime well under 20 min
SUCCESS_SCORE_THRESHOLD = 0.3

# ── Clients ───────────────────────────────────────────────────────────────────
# Auto-detect Groq models — use OpenAI client with Groq base URL
_GROQ_MODELS = {"llama-3.3-70b-versatile","llama-3.1-8b-instant","llama3-70b-8192",
                "llama3-8b-8192","mixtral-8x7b-32768","gemma2-9b-it","gemma-7b-it"}
_GROQ_BASE_URL = "https://api.groq.com/openai/v1"

def _is_groq(model: str) -> bool:
    return model in _GROQ_MODELS or model.startswith(("llama","mixtral","gemma"))

_api_key = OPENAI_API_KEY or HF_TOKEN or "no-key"
if _is_groq(MODEL_NAME):
    openai_client = OpenAI(api_key=_api_key, base_url=_GROQ_BASE_URL)
    print(f"Provider: Groq ({MODEL_NAME})", flush=True)
else:
    openai_client = OpenAI(api_key=_api_key)
    print(f"Provider: OpenAI ({MODEL_NAME})", flush=True)

http = httpx.Client(base_url=API_BASE_URL, timeout=60.0)

# Global timeout guard — 18 min hard cap
INFERENCE_START = time.time()
MAX_TOTAL_SECONDS = 18 * 60

# ── Mandatory log helpers (exact format — do not change) ──────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Sanitize action string — no spaces or newlines inside
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

# ── Agent ─────────────────────────────────────────────────────────────────────

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

            # Get action from LLM
            try:
                action_dict = get_agent_action(history, obs)
            except Exception as e:
                action_dict = {"agent": "debugger", "action_type": "search_logs", "command": "ERROR"}
                last_error = str(e)

            action_str = action_dict.get("action_type", "unknown")

            # Execute in environment
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

            log_step(
                step=step,
                action=action_str,
                reward=step_reward,
                done=done,
                error=last_error,
            )

            if done:
                score = float(reward_data.get("total", 0.0))
                break

        # Force submit if not done
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

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return {
        "task_id": task_id,
        "score": score,
        "steps": steps_taken,
        "success": success,
        "rewards": rewards,
    }

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"InfraMind Baseline Inference | API={API_BASE_URL} | MODEL={MODEL_NAME} | SEED={INFERENCE_SEED}", flush=True)

    # Verify environment is reachable
    try:
        r = http.get("/health")
        r.raise_for_status()
        print(f"Environment: {r.json().get('service')} v{r.json().get('version')} — OK", flush=True)
    except Exception as e:
        print(f"ERROR: Cannot reach {API_BASE_URL}: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for task_id in TASK_IDS:
        try:
            result = run_task(task_id)
            results.append(result)
        except Exception as e:
            print(f"ERROR running {task_id}: {e}", file=sys.stderr)
            results.append({"task_id": task_id, "score": 0.0, "steps": 0, "success": False, "rewards": []})

    # Summary
    avg_score = sum(r["score"] for r in results) / max(len(results), 1)
    print(f"\n{'='*55}", flush=True)
    print(f"INFRA MIND BASELINE — Model: {MODEL_NAME}", flush=True)
    for r in results:
        grade = "S" if r["score"] >= 0.9 else "A" if r["score"] >= 0.7 else "B" if r["score"] >= 0.5 else "C" if r["score"] >= 0.3 else "F"
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['task_id']:22s}  score={r['score']:.3f}  steps={r['steps']}  grade={grade}", flush=True)
    print(f"  {'AVERAGE':24s}  score={avg_score:.3f}", flush=True)
    print(f"{'='*55}", flush=True)


if __name__ == "__main__":
    main()
