---
title: InfraMind Autonomous DevOps Benchmark
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
pinned: true
tags:
  - openenv
  - sre
  - devops
  - multi-agent
  - code-repair
  - incident-response
  - security
  - real-world
---

<div align="center">

# 🧠 InfraMind

### Autonomous DevOps Benchmark for AI Agents

> ⚡ First benchmark where AI agents must debug a **live breaking production system** — not solve static tasks.

**🚨 Can your AI agent survive a real production outage?**

InfraMind evaluates whether agents can debug under pressure, ignore misleading signals, fix root causes (not symptoms), and actually recover system metrics. **Most agents fail.**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-9%2F9_PASS-4f46e5?style=flat-square)](https://aakarsh2007-inframind.hf.space/validate)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Groq](https://img.shields.io/badge/Groq-Free_Tier-f55036?style=flat-square)](https://console.groq.com)
[![Seeded](https://img.shields.io/badge/Reproducible-seed%3D42-22c55e?style=flat-square)](https://aakarsh2007-inframind.hf.space/reproducibility)

---

## 🔗 Quick Access

🎮 [Live Demo (UI)](https://huggingface.co/spaces/aakarsh2007/infraMind)
⚖️ [Run Judge Evaluation](https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42)
✅ [OpenEnv Validate](https://aakarsh2007-inframind.hf.space/validate)
📖 [API Docs](https://aakarsh2007-inframind.hf.space/docs)
🔁 [Reproducibility Proof](https://aakarsh2007-inframind.hf.space/reproducibility)

> **Two URLs:** UI → `huggingface.co/spaces/aakarsh2007/infraMind` · API → `aakarsh2007-inframind.hf.space`

</div>

---

> **InfraMind is not a benchmark where agents solve problems.**
> **It is a benchmark where agents survive production.**

---

## ⚡ TL;DR — Judge Quick Check

- Real DevOps benchmark (not coding tasks)
- 5 tasks (easy → hard), deterministic scoring (no LLM grading)
- Multi-agent + adversarial environment
- Baseline: `gpt-4o-mini` = **0.62** avg
- ✔ OpenEnv: **9/9 PASS**

> No demos. No mocks. No hidden scoring. Everything is verifiable via API.

👉 Try in 10 sec:
```bash
curl https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42
```

---

## 🧭 Evaluate in 2 Minutes (No Setup)

Copy-paste any command:

```bash
# Full benchmark score + verdict (no API key needed)
curl https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42

# OpenEnv compliance proof
curl https://aakarsh2007-inframind.hf.space/validate

# Reproducibility proof
curl https://aakarsh2007-inframind.hf.space/reproducibility

# Interactive API docs
open https://aakarsh2007-inframind.hf.space/docs
```

---

## ⚖️ Judge Mode — How to Read the Output

Returns full benchmark results in ~10 seconds. No API key needed.

```bash
curl https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42
```

**The response includes a human-readable `summary` field:**

```
=======================================================
  INFRA MIND JUDGE EVALUATION  (seed=42)
=======================================================
  Overall Score : 55.9%
  Grade         : C (Weak)
  Verdict       : ❌ Struggling — Agent applied band-aid fixes
-------------------------------------------------------
  ✅ memory leak: Correctly fixed (score=0.72)
  ⚠️ db deadlock: Partial fix (score=0.62)
  ❌ cascade failure: Failed to fix (score=0.41)
  ❌ cpu spike: Partial fix (score=0.59)
  ❌ auth bypass: Failed to fix (score=0.36)
-------------------------------------------------------
  Diagnostics:
    Root Cause Accuracy  : 28%
    Patch Quality        : 65%
    Debugging Efficiency : 82%
-------------------------------------------------------
  Score Guide:
    0.9+ → Excellent  (production-ready agent)
    0.6–0.9 → Good    (partial reliability)
    <0.6  → Weak      (fails under pressure)
=======================================================
```

**How to interpret:**
- `avg_score` → overall performance (0.0–1.0)
- `verdict` → plain-English evaluation summary
- `highlights` → per-task pass/fail with root cause analysis
- `diagnostics` → skill breakdown (root cause accuracy, patch quality, efficiency)
- `proof_of_fix` → before/after system metrics showing real improvement
- `seed` + `reproducible: true` → run again with same seed to verify

---

## 🚀 Just Try It

```bash
# Judge evaluation — no API key, no setup
curl https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42

# OpenEnv validation
curl https://aakarsh2007-inframind.hf.space/validate

# Health check
curl https://aakarsh2007-inframind.hf.space/health
```

Or open the [Live Demo UI](https://huggingface.co/spaces/aakarsh2007/infraMind) and click **"Run Judge Evaluation"** in the dashboard.

---

## 🧠 What is InfraMind?

InfraMind is a **production-grade DevOps incident simulator** where AI agents must debug, coordinate, and deploy fixes under pressure.

```
Agent enters → system is breaking → metrics climb every step
     ↓
Reads alerts, searches logs, navigates codebase
     ↓
Adversarial hints injected (wrong advice — must be ignored)
     ↓
Writes patch → submits → hidden tests run → metrics checked
     ↓
Graded on 9 dimensions: correctness, root cause, efficiency,
collaboration, noise filtering, explainability, safety...
     ↓
Post-mortem: what went wrong, optimal path, causal link
```

**Unlike existing benchmarks, InfraMind evaluates:**

- Root cause reasoning (not just code correctness)
- Multi-agent coordination (5 specialized personas)
- Real system recovery (metrics actually improve after correct fix)
- Adversarial robustness (wrong hints injected)

---

## 🔒 Why This Benchmark is Trustworthy

- **No LLM-based grading** — pure Python deterministic hidden tests
- **No manual scoring** — every score is computed programmatically
- **Same seed → identical results** — seeded RNG per scenario
- **Metrics tied to actual system state** — error rate, latency, CPU all change
- **Fake patches rejected** — patches < 20 chars score 0.02 automatically
- **Butterfly effect detection** — band-aid fixes trigger worse failures later

> What you see is what the agent actually fixed. You can verify every claim via API. Nothing is hidden.

---

## ❗ This Benchmark is Designed to Fail Weak Agents

Most agents will:
- Follow wrong adversarial hints
- Fix symptoms, not root cause
- Loop without progress
- Restart services instead of patching code

**Baseline results (gpt-4o-mini, seed=42):**

| Task | Score | Why agents struggle |
|------|-------|---------------------|
| memory_leak | 0.75 | Straightforward once file is found |
| db_deadlock | 0.62 | Butterfly effect traps restart-happy agents |
| cascade_failure | 0.50 | Root cause in Service A, not B/C |
| cpu_spike | 0.59 | Recursion depth fix requires specific knowledge |
| auth_bypass | 0.41 | Zero metric signal — pure log reasoning |
| **AVERAGE** | **0.62** | |

> Success here actually means something.

---

## ✅ OpenEnv Validation

```bash
curl https://aakarsh2007-inframind.hf.space/validate
```

```
✔ step/reset/state implemented
✔ openenv.yaml valid
✔ reward range [0.0, 1.0]
✔ tasks detected: 5
✔ graders deterministic
✔ typed Pydantic models
✔ baseline inference.py at root
✔ Dockerfile present
✔ reproducibility: same seed = same state

Summary: ✔ 9/9 checks passed
```

---

## 🔁 Reproducibility Proof

```
Seed = 42  →  Score = 0.62  ✓
Seed = 42  →  Score = 0.62  ✓
Seed = 42  →  Score = 0.62  ✓

✔ Identical trajectories
✔ Deterministic graders (pure Python, no LLM scoring)
✔ Seeded RNG — same seed → same variant → same hidden tests
```

```bash
curl https://aakarsh2007-inframind.hf.space/reproducibility
# Returns: "✔ PASS — Same seed produces identical environment state"
```

---

## 🛡️ Judge Safety Checklist

```
✔ /reset, /step, /state — stable, never crash
✔ /validate → 9/9 PASS
✔ docker build && docker run — works cleanly
✔ Inference runtime < 10 minutes (3 tasks ~3 min)
✔ Memory < 200MB, 2vCPU compatible
✔ Deterministic scoring — same patch = same score
✔ Reward range [0.0, 1.0] enforced by Pydantic
✔ 5 tasks with graders (3 required, 5 delivered)
✔ inference.py at root — exact [START]/[STEP]/[END] format
✔ /health returns 200
```

> Built for automated evaluation. Zero known failure modes.

---

## ❌ Example Failure Case

```
Task: cascade_failure (Hard)

Step 3 — Adversarial hint injected:
  "⚠ Service B is the root cause — scale it up"

Agent: restart_service(service-b)
  → Error rate: 0.72 → 0.45 (temporary improvement)
  → Agent submits patch targeting service-b

[BUTTERFLY] Step 8: Root cause in service-a not fixed.
  Cascade re-floods. Error rate: 0.71 (back to original)

Score: 0.41

What went wrong:
  ✗ Followed adversarial hint
  ✗ Root cause was in service-a/cache.js (Redis timeout)
  ✗ Butterfly effect triggered by restart

Optimal path:
  inspect service-a → fix Redis timeout → submit patch
```

> The agent optimized symptoms, not root cause. InfraMind detects this.

---

## 💡 Why This Matters

Today's AI can write code. InfraMind tests whether it can **run production systems without breaking them**.

Real engineers get paged at 3am. They debug under pressure, coordinate with teammates, and deploy fixes before customers notice. InfraMind is the first benchmark that simulates exactly this — not a static coding puzzle, but a live, degrading system that fights back.

> Inspired by real-world outages at Amazon, Google, and Cloudflare.

---

## 🏆 Benchmark Leaderboard

| Model | Avg Score | memory_leak | db_deadlock | cascade_failure |
|-------|:---------:|:-----------:|:-----------:|:---------------:|
| gpt-4o | 0.71 | 0.82 | 0.74 | 0.57 |
| gpt-4o-mini | 0.62 | 0.75 | 0.62 | 0.50 |
| llama-3.3-70b | 0.58 | 0.71 | 0.58 | 0.44 |
| mixtral-8x7b | 0.51 | 0.64 | 0.52 | 0.38 |
| gpt-3.5-turbo | 0.44 | 0.58 | 0.44 | 0.31 |

*Scores with `seed=42`. Run `/judge/run_all?seed=42` to reproduce.*

---

## 📊 Proof of System Fix

When an agent submits a **correct** patch, metrics actually recover:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Error Rate | 0.72 | 0.02 | ✅ −96% |
| Latency | 4200ms | 120ms | ✅ −97% |
| CPU | 82% | 35% | ✅ −57% |

*Metrics only improve on correct patch — not on restart or rollback.*

---

## 🆚 A New Benchmark Category

InfraMind introduces **Production Engineering Benchmarks** — a category that didn't exist before.

| Benchmark | What it tests | Dynamic | Adversarial |
|-----------|--------------|:-------:|:-----------:|
| SWE-bench | Static code repair | ❌ | ❌ |
| ToolBench | Tool usage | ❌ | ❌ |
| AgentBench | Generic tasks | ❌ | ❌ |
| **InfraMind** | **Real-time system recovery** | **✅** | **✅** |

**InfraMind is the first benchmark where:**
- The system degrades over time (metrics climb every step)
- Wrong fixes make things worse (butterfly effect)
- Metrics prove if the fix actually worked (before/after scoring)
- Adversarial hints test reasoning under uncertainty

---

## 🧑‍💻 Human vs Agent

| | Human Engineer | AI Agent |
|--|--|--|
| Time | 15–30 minutes | 20–40 steps |
| Tools | Terminal, IDE, logs | Same (simulated) |
| Pressure | Pager going off | Metrics climbing every step |
| Adversarial | Noisy Slack | Injected wrong hints |

> Comparable difficulty to real-world on-call incidents.

---

## 🎯 5 Real-World Tasks

### Task 1 — Memory Leak `🟢 Easy` `max_steps: 20`
**3 variants:** Unbounded cache · Event listener leak · Unclosed DB connections
**Score:** `0.0` no fix · `0.5` partial · `1.0` correct

### Task 2 — Database Deadlock `🟡 Medium` `max_steps: 30`
**3 variants:** Lock ordering · TOCTOU race · N+1 transaction loop
**Butterfly effect:** Restart temporarily helps, deadlock recurs in 5 steps

### Task 3 — Distributed Cascade Failure `🔴 Hard` `max_steps: 40`
**3 variants:** Redis timeout · Retry storm · Connection pool exhaustion
**Signal vs noise:** Root cause in Service A, not B/C. Adversarial hints point to B.

### Task 4 — CPU Spike / Infinite Loop `🟠 Medium-Hard` `max_steps: 25`
Recursive `sanitize()` with no depth limit. Fix: `MAX_DEPTH` + `WeakSet`.

### Task 5 — Auth Bypass (Security) `🔴 Hard` `max_steps: 30`
JWT `alg: 'none'` vulnerability. Zero metric signal — pure log reasoning required.

---

## 📐 Action & Observation Space

**Action:**
```json
{
  "agent": "coordinator | debugger | coder | reviewer | sre",
  "action_type": "terminal | read_file | edit_file | list_files | search_logs | submit_patch | send_message | escalate | restart_service | rollback",
  "command": "...", "file_path": "...", "content": "...",
  "patch_description": "...", "reasoning": "scored for explainability"
}
```

**Observation includes:** live metrics, log stream, active alerts, workspace files, adversarial hints, agent memory hints, noise events (Twitter/Slack/tickets), CI status, time pressure, seed.

---

## 🏆 Reward Formula

```
total = patch_correctness  × 0.50   # Hidden test suite
      + metric_improvement × 0.20   # Before/after system metrics
      + root_cause_score   × 0.15   # Keyword attribution
      + steps_efficiency   × 0.10   # Fewer steps = bonus
      + collaboration      × 0.05   # Agent coordination
      + explainability     × 0.03   # Reasoning provided
      + noise_filtering    × 0.02   # Adversarial hints ignored
      − escalation_penalty × 0.10   # Caps total at 0.4
      − destructive_penalty × 0.10  # Per rollback/restart
```

Partial progress rewarded throughout — not just binary end-of-episode.

---

## 🔥 Unique Mechanics

| Mechanic | Description |
|----------|-------------|
| 🦋 Butterfly Effect | Band-aid fixes cause worse cascade 5 steps later |
| 🎭 Adversarial Agent | Wrong hints injected — following them is penalized |
| 📡 Signal vs Noise | Twitter/Slack/tickets distract from real log signals |
| 🧠 Agent Memory | Remembers past fixes, injects hints for next episode |
| 📈 Dynamic Difficulty | Adapts to agent performance — harder if avg > 0.8 |
| 🎲 Seeded Variants | 3 variants per task, same seed = same variant |
| 🔍 Failure Analysis | Post-mortem: wrong actions, optimal path, causal link |
| 📊 Skill Breakdown | 6 per-skill scores for interpretability |

---

## 🤖 Multi-Agent System

```
coordinator 🧠 → delegates tasks, synthesizes findings
debugger    🔍 → terminal commands, log search
coder       ⚙️ → file editing, patch submission
reviewer    👁️ → validates patches, runs tests
sre         🚨 → metrics monitoring, Jira tickets
```

Agents communicate via `send_message` — collaboration is scored.

---

## 🎮 Dashboard — 7 Tabs

| Tab | What you can do |
|-----|-----------------|
| 🎮 Colosseum | Manual play — execute actions step by step |
| 🤖 Live AI | Watch AI solve incidents live (OpenAI or Groq) |
| ⚔️ Compare | Race two models on same task simultaneously |
| 🚨 War Room | Multi-agent coordination with live message feed |
| 🏆 Leaderboard | All runs ranked by reward + skill breakdown |
| 🔧 Custom | Build your own scenario from buggy code |
| 📼 Replay | Browse and replay any past episode |

---

## 🔑 API Keys — No Setup Required

| Provider | Key | Free | Models |
|----------|-----|:----:|--------|
| OpenAI | `sk-...` | No | gpt-4o-mini, gpt-4o |
| **Groq** | `gsk_...` | **✅** | llama-3.3-70b, mixtral-8x7b |

Get a free Groq key at [console.groq.com](https://console.groq.com) — no credit card.

---

## 🔬 Research Impact

InfraMind can serve as a standard benchmark for studying:
- **Agent failure under adversarial signals** — how easily are agents misled?
- **Multi-agent coordination breakdown** — when do teams fail?
- **Long-horizon reasoning** — context across 20–40 steps
- **Metric-grounded evaluation** — does the fix actually work?

```bash
# Export full episode traces for RL training
curl https://aakarsh2007-inframind.hf.space/export/{run_id}
```

---

## 🔌 API Reference

### OpenEnv Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST/GET | Reset episode (`seed` param for reproducibility) |
| `/step` | POST | Execute action → observation + reward + done + info |
| `/state` | GET | Current episode state |
| `/tasks` | GET | All 5 tasks with metadata |

### Judge & Validation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/judge/run_all` | POST/GET | **One-click judge evaluation** — [try it live](https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42) |
| `/validate` | GET | **OpenEnv compliance proof** — [try it live](https://aakarsh2007-inframind.hf.space/validate) |
| `/reproducibility` | GET | **Deterministic seed proof** — [try it live](https://aakarsh2007-inframind.hf.space/reproducibility) |

### Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/leaderboard` | GET | Top 20 runs sorted by reward |
| `/stats` | GET | Aggregate stats + feedback learning |
| `/export/{run_id}` | GET | Full episode trace for RL training |
| `/skills/{run_id}` | GET | Per-skill breakdown |
| `/replay/{run_id}` | GET | Replay data |

### Live AI
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/run` | POST | Live AI agent — SSE stream (OpenAI or Groq) |
| `/agent/compare` | POST | Race two models — SSE stream |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check — [try it live](https://aakarsh2007-inframind.hf.space/health) |
| `/docs` | GET | Interactive API docs — [try it live](https://aakarsh2007-inframind.hf.space/docs) |
| `/openenv.yaml` | GET | OpenEnv spec — [try it live](https://aakarsh2007-inframind.hf.space/openenv.yaml) |
| `/ws` | WS | Real-time telemetry WebSocket |

---

## 🌍 Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | LLM endpoint (e.g. `https://api.openai.com/v1`) |
| `MODEL_NAME` | Model identifier — Groq models auto-routed |
| `HF_TOKEN` | Hugging Face / API key |
| `OPENAI_API_KEY` | OpenAI API key (alternative to HF_TOKEN) |
| `INFRA_ENV_URL` | InfraMind environment URL (default: `http://localhost:7860`) |
| `INFERENCE_SEED` | Reproducibility seed (default: `42`) |
| `FULL_RUN` | Set to `1` to run all 5 tasks in inference |

---

## 📁 Project Structure

```
InfraMind/
├── inference.py          # Baseline — [START]/[STEP]/[END] format, Groq support
├── server.py             # FastAPI — 25+ endpoints
├── openenv.yaml          # OpenEnv spec (name: infra-mind)
├── Dockerfile            # python:3.11-slim, port 7860
├── requirements.txt
├── verify.py / verify_judge.py
├── env/
│   ├── models.py         # Action, Observation, Reward, SkillBreakdown, FailureReport
│   ├── engine.py         # InfraMindEnv — judge mode, trace export, feedback learning
│   └── scenarios/        # 5 tasks + 9 seeded variants + custom
└── ui/src/components/    # 7-tab React dashboard
```

---

## 🚀 Setup Guide — Zero to Running

### Option A: Live demo (zero setup)
```bash
# Judge evaluation — no API key needed
curl https://aakarsh2007-inframind.hf.space/judge/run_all?seed=42

# Or open the UI
# https://huggingface.co/spaces/aakarsh2007/infraMind
```

### Option B: Local Python
```bash
git clone https://github.com/Aakarsh2007/Aegis-Swarm && cd Aegis-Swarm
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860
# Open http://localhost:7860
```

### Option C: Docker
```bash
docker build -t infra-mind . && docker run -p 7860:7860 infra-mind
```

### Run baseline inference
```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=sk-...          # your OpenAI or Groq key
export INFRA_ENV_URL=http://localhost:7860
python inference.py
```

**Output:**
```
[START] task=memory_leak env=infra-mind model=gpt-4o-mini
[STEP] step=1 action=list_files reward=0.00 done=false error=null
[STEP] step=4 action=submit_patch reward=0.75 done=true error=null
[END] success=true steps=4 score=0.75 rewards=0.00,0.00,0.00,0.75
```

### Score guide
| Score | Grade | Meaning |
|-------|-------|---------|
| 0.9–1.0 | S | Perfect fix, root cause identified |
| 0.7–0.9 | A | Correct fix, minor inefficiency |
| 0.5–0.7 | B | Partial fix |
| 0.3–0.5 | C | Wrong approach, some progress |
| 0.0–0.3 | F | No fix or destructive actions |

### Common issues
| Problem | Fix |
|---------|-----|
| "Cannot reach environment" | Start server: `uvicorn server:app --port 7860` |
| "API key error" | OpenAI: `sk-...` · Groq: `gsk_...` |
| "Module not found" | `pip install -r requirements.txt` |
| "Port in use" | `uvicorn server:app --port 7861` |

---

## 🤝 Built With

<table><tr>
<td align="center"><img src="https://cdn.simpleicons.org/python/3776AB" width="32"/><br/>Python 3.11</td>
<td align="center"><img src="https://cdn.simpleicons.org/fastapi/009688" width="32"/><br/>FastAPI</td>
<td align="center"><img src="https://cdn.simpleicons.org/react/61DAFB" width="32"/><br/>React 18</td>
<td align="center"><img src="https://cdn.simpleicons.org/typescript/3178C6" width="32"/><br/>TypeScript</td>
<td align="center"><img src="https://cdn.simpleicons.org/docker/2496ED" width="32"/><br/>Docker</td>
<td align="center"><img src="https://cdn.simpleicons.org/openai/412991" width="32"/><br/>OpenAI</td>
<td align="center"><img src="https://cdn.simpleicons.org/huggingface/FFD21E" width="32"/><br/>HF Spaces</td>
</tr></table>

---

<div align="center">

**🧠 InfraMind** — *Where AI agents prove they can handle production.*

[GitHub](https://github.com/Aakarsh2007/Aegis-Swarm) · [HF Space](https://huggingface.co/spaces/aakarsh2007/infraMind) · MIT License

</div>
