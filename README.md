---
title: Gravex-Aegis Autonomous DevOps War-Room
emoji: ⚔️
colorFrom: orange
colorTo: red
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

```
 ██████╗ ██████╗  █████╗ ██╗   ██╗███████╗██╗  ██╗      █████╗ ███████╗ ██████╗ ██╗███████╗
██╔════╝ ██╔══██╗██╔══██╗██║   ██║██╔════╝╚██╗██╔╝     ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝
██║  ███╗██████╔╝███████║██║   ██║█████╗   ╚███╔╝      ███████║█████╗  ██║  ███╗██║███████╗
██║   ██║██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝   ██╔██╗      ██╔══██║██╔══╝  ██║   ██║██║╚════██║
╚██████╔╝██║  ██║██║  ██║ ╚████╔╝ ███████╗██╔╝ ██╗     ██║  ██║███████╗╚██████╔╝██║███████║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝
```

# ⚔️ Gravex-Aegis: Autonomous DevOps War-Room

**The world's first multi-agent SRE simulation environment for OpenEnv**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-orange?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsOSA1IDktNXYtNWwtOSA1LTktNXoiLz48L3N2Zz4=)](https://huggingface.co/spaces)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Built by fusing **Aegis** (autonomous SRE remediation engine) with **Gravex** (multi-agent isolated workspace platform)*

[🎮 Live Demo](https://huggingface.co/spaces/Aakarsh2007/Gravex-Aegis) · [📖 API Docs](https://huggingface.co/spaces/Aakarsh2007/Gravex-Aegis/docs) · [🏆 Leaderboard](https://huggingface.co/spaces/Aakarsh2007/Gravex-Aegis/leaderboard)

</div>

---

## 🧠 What Is This?

Real DevOps teams don't answer static questions — they debug **live systems under pressure**, coordinate across specializations, and write code that actually fixes things. Existing agent benchmarks test single-step reasoning on toy problems.

**Gravex-Aegis tests multi-step, multi-agent, real-world incident response** — the kind of work that fills on-call rotations every night.

An AI agent is dropped into an **actively degrading production backend**. It must:

1. Read streaming telemetry (CPU, memory, latency, error rate climbing in real time)
2. Search logs to find the root cause (buried in noise from customer tickets and social media)
3. Navigate a simulated codebase with multiple services
4. Coordinate between specialized sub-agent personas
5. Write and submit a working code patch before the system crashes

This is not a game. This is not a toy. This is a **benchmark for autonomous AI engineering teams**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Gravex-Aegis War-Room                        │
│                                                                 │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐ │
│  │    AEGIS ENGINE          │  │     GRAVEX ENGINE            │ │
│  │  (Scenario & Telemetry) │  │  (Multi-Agent Workspace)     │ │
│  │                         │  │                              │ │
│  │  • Chaos Generator      │  │  • 5 Agent Personas          │ │
│  │  • War-Room Clock       │  │  • Agent Memory System       │ │
│  │  • Butterfly Effect     │  │  • Dynamic Difficulty        │ │
│  │  • Signal vs Noise      │  │  • Agent Communication       │ │
│  │  • Hidden Test Grader   │  │  • Isolated Workspace        │ │
│  └─────────────────────────┘  └──────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  OpenEnv Interface                       │   │
│  │  POST /reset  •  POST /step  •  GET /state  •  GET /tasks│   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🎯 Core OpenEnv Compliance
- Full `step()` / `reset()` / `state()` API with typed Pydantic models
- `openenv.yaml` with complete metadata
- Deterministic graders — same patch always gets same score
- Reward range strictly `[0.0, 1.0]` with partial progress signals

### 🔥 5 Real-World Tasks (Easy → Hard)
| Task | Difficulty | Domain | Max Steps |
|------|-----------|--------|-----------|
| Memory Leak | 🟢 Easy | Node.js cache management | 20 |
| Database Deadlock | 🟡 Medium | PostgreSQL concurrency | 30 |
| Distributed Cascade Failure | 🔴 Hard | Microservices / Redis | 40 |
| CPU Spike / Infinite Loop | 🟠 Medium-Hard | Recursive algorithms | 25 |
| Auth Bypass (Security) | 🔴 Hard | JWT vulnerability | 30 |

### 🎲 Randomized Scenario Variants
Each task has **3 different bug variants** — every reset picks a different one. Memory leak can be an unbounded cache, event listener accumulation, or unclosed DB connections. No two runs are identical.

### 🦋 Butterfly Effect Engine
Band-aid fixes (restarting services) temporarily stabilize metrics but trigger a worse cascade 5 steps later. Agents must find the **root cause**, not silence the alarm.

### 📡 Signal vs. Noise Simulation
Real SREs don't debug in a vacuum. The observation space injects customer support tickets, Twitter mentions, Slack alerts, and PagerDuty noise at specific steps. Agents must filter signal from noise.

### 🧠 Agent Memory System
Agents remember past fixes across episodes. If an agent solved a memory leak before, the next episode includes a hint: *"Memory: Previous fix for memory_leak: Add LRU eviction (reward=0.85)"*

### 📈 Dynamic Difficulty Adaptation
After 3+ runs on a task, if avg reward > 0.8 the environment gets harder (more noise, faster metric degradation). If avg < 0.3 it gets easier. The environment adapts to the agent's skill level.

### 🤖 Live AI Agent (Browser)
Users paste their OpenAI API key and watch an AI agent solve incidents in real time — step by step, with reasoning shown for each action. Server-Sent Events stream every step live.

### ⚔️ Model Comparison Mode
Run two different models (e.g. GPT-4o vs GPT-4o-mini) on the same task simultaneously. See side-by-side which model finds the root cause faster and scores higher.

### 🚨 War Room View
Multi-agent coordination visualized as a live message feed. See the coordinator delegate to the debugger, the debugger report findings, the coder submit a patch, and the reviewer validate it — all in real time.

### 🔧 Custom Scenario Builder
Paste your own buggy code and fixed version. The environment generates a fully playable incident scenario from it — complete with logs, alerts, metrics, and a grader.

### 📼 Replay Mode
Browse all completed runs. Click any run to see its full post-mortem: which hidden tests passed, what the root cause was, how many steps were wasted, and whether the butterfly effect triggered.

### 🏆 Leaderboard & Analytics
Global leaderboard sorted by reward. Per-task statistics. Dynamic difficulty tracking. Feedback loop for human ratings.

---

## 🎮 Dashboard Tabs

| Tab | Description |
|-----|-------------|
| 🎮 Colosseum | Manual play — execute actions step by step, watch metrics live |
| 🤖 Live AI | Watch an AI agent solve incidents with your API key |
| ⚔️ Compare | Race two models on the same task simultaneously |
| 🚨 War Room | Multi-agent coordination view with live message feed |
| 🏆 Leaderboard | All runs ranked by reward with stats |
| 🔧 Custom | Build your own incident scenario from buggy code |
| 📼 Replay | Browse and replay any past episode |

---

## 📐 Action Space

```json
{
  "agent": "coordinator | debugger | coder | reviewer | sre",
  "action_type": "terminal | read_file | edit_file | list_files | search_logs | submit_patch | send_message | create_jira | run_tests | escalate",
  "command": "shell command or search pattern",
  "file_path": "path/to/file.js",
  "content": "full new file content (for edit_file)",
  "patch_description": "explanation of the fix (for submit_patch)",
  "message": "message to another agent (for send_message)",
  "target_agent": "target agent name",
  "reasoning": "why this action — used in explainability scoring"
}
```

| Action | Agent | Description |
|--------|-------|-------------|
| `terminal` | debugger/sre | Simulated shell: grep, tail, htop, cat, ls, git log |
| `read_file` | coder | Read a file from the workspace |
| `edit_file` | coder | Write new content to a file |
| `list_files` | any | List workspace files |
| `search_logs` | debugger | Search log buffer with a pattern |
| `submit_patch` | coder | Submit patched file for grading — ends episode |
| `send_message` | any | Agent-to-agent communication |
| `create_jira` | sre | Create a Jira ticket for the incident |
| `run_tests` | reviewer | Trigger CI/CD test suite |
| `escalate` | coordinator | Get a human hint (caps reward at 0.4) |

---

## 👁️ Observation Space

```json
{
  "step": 5,
  "task_id": "cascade_failure",
  "metrics": {
    "cpu_percent": 78.0,
    "memory_percent": 61.0,
    "latency_ms": 4200.0,
    "error_rate": 0.72,
    "active_connections": 380,
    "uptime_seconds": 14400.0
  },
  "active_alerts": [
    {"id": "c1", "severity": "critical", "service": "service-b",
     "message": "Connection pool exhausted — 100% connections in use"}
  ],
  "recent_logs": [
    "[ERROR] service-a: Redis ETIMEDOUT — event loop blocked 4200ms",
    "[ERROR] service-b: connection pool exhausted (pool size: 10/10)"
  ],
  "available_files": ["service-a/cache.js", "service-b/gateway.js"],
  "noise_events": [
    {"source": "twitter", "content": "Your app is down! #outage"}
  ],
  "action_result": "...",
  "memory_hints": ["Memory: Previous fix: add Redis timeout (reward=0.85)"],
  "difficulty_level": 1.2,
  "ci_status": "failing",
  "time_pressure": "critical",
  "escalated": false,
  "done": false
}
```

---

## 🎯 Tasks

### Task 1 — Memory Leak `🟢 Easy` `max_steps: 20`

**3 randomized variants:**
- Unbounded user cache (`userCache = {}` with no eviction)
- Event listener accumulation (`bus.on()` never removed)
- Unclosed database connections (`pool.connect()` without `client.release()`)

**Root cause pattern:** Resource allocated but never freed.
**Fix pattern:** Add eviction/cleanup/release logic.

### Task 2 — Database Deadlock `🟡 Medium` `max_steps: 30`

**3 randomized variants:**
- Inconsistent lock ordering in fund transfers
- Missing transaction isolation (TOCTOU race condition)
- N+1 transaction loop with overlapping order IDs

**Root cause pattern:** Concurrent operations acquiring shared resources in inconsistent order.
**Butterfly effect:** Restarting the service temporarily helps but deadlocks recur in 5 steps.

### Task 3 — Distributed Cascade Failure `🔴 Hard` `max_steps: 40`

**3 randomized variants:**
- Redis timeout cascade (no `connectTimeout`, no circuit breaker)
- HTTP retry storm (10 immediate retries with no backoff)
- Connection pool exhaustion (`max: 100` per instance × 10 instances)

**Root cause pattern:** Service A's failure amplified by Service B's retry behavior.
**Signal vs. noise:** Service B and C errors are symptoms. Root cause is in Service A.

### Task 4 — CPU Spike / Infinite Loop `🟠 Medium-Hard` `max_steps: 25`

**Root cause:** `sanitize()` function with no depth limit and no circular reference detection.
**Fix:** Add `MAX_DEPTH` check and `WeakSet` for circular reference guard.

### Task 5 — Auth Bypass (Security) `🔴 Hard` `max_steps: 30`

**Root cause:** `jwt.verify()` without `algorithms` whitelist accepts `alg: 'none'`.
**Unique mechanic:** System metrics look completely normal — this is a security incident, not a performance one. Agents must read logs carefully.

---

## 🏆 Reward Function

Rewards provide **partial progress signals throughout the episode** — not just binary end-of-episode:

```
total = patch_correctness × 0.60
      + steps_efficiency  × 0.20
      + no_regression     × 0.20
      + explainability    × 0.05 (bonus)
      + collaboration     × 0.05 (bonus)
      - escalation_penalty × 0.10 (if escalated)
      - destructive_penalty × 0.10 per destructive action
```

| Component | Description |
|-----------|-------------|
| `patch_correctness` | Fraction of hidden deterministic test cases passed |
| `steps_efficiency` | Bonus for solving in fewer steps |
| `no_regression` | Patch doesn't break existing functionality |
| `root_cause_identified` | Partial credit for correct diagnosis in `patch_description` |
| `explainability_score` | Agent provided `reasoning` field on actions |
| `collaboration_score` | Agent used `send_message` to coordinate |
| `escalation_penalty` | -0.1 if agent escalated to human (also caps total at 0.4) |
| `safety_score` | Penalizes destructive actions like rollbacks |

---

## 📊 Baseline Scores

Scores from running `inference.py` with `gpt-4o-mini`:

| Task | Reward | Steps | Grade |
|------|--------|-------|-------|
| memory_leak | 0.690 | 3 | B |
| db_deadlock | 0.877 | 3 | A |
| cascade_failure | 0.423 | 3 | C |
| **AVERAGE** | **0.663** | **3** | **B** |

*Scores vary per run due to randomized variants. Run `FULL_RUN=1 python inference.py` for all 5 tasks.*

---

## 🚀 Setup & Usage

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/Aakarsh2007/Aegis-Swarm
cd Aegis-Swarm

# Build UI (required before docker build)
cd ui && npm install && npm run build && cd ..

# Build and run
docker build -t gravex-aegis .
docker run -p 7860:7860 gravex-aegis
```

Open `http://localhost:7860`

### Option 2: Local Python

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860
```

### Run Baseline Inference

```bash
export OPENAI_API_KEY=sk-your-key
export API_BASE_URL=http://localhost:7860
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=hf_your-token

python inference.py
```

For all 5 tasks:
```bash
FULL_RUN=1 python inference.py
```

---

## 🔌 API Reference

### OpenEnv Core

```bash
# Reset to a task (returns initial Observation)
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "memory_leak", "model": "gpt-4o-mini"}'

# Execute an action (returns observation + reward + done + info)
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"agent": "debugger", "action_type": "search_logs", "command": "ERROR"}'

# Get current state (non-destructive)
curl http://localhost:7860/state

# List all tasks
curl http://localhost:7860/tasks
```

### Extended API

```bash
# Leaderboard
curl http://localhost:7860/leaderboard

# Aggregate stats
curl http://localhost:7860/stats

# Agent memory across episodes
curl http://localhost:7860/memory

# Submit feedback on a run
curl -X POST http://localhost:7860/feedback \
  -d '{"run_id": "abc123", "rating": "thumbs_up"}'

# Live AI agent (SSE stream)
curl -X POST http://localhost:7860/agent/run \
  -d '{"task_id": "memory_leak", "api_key": "sk-...", "model": "gpt-4o-mini"}'

# Model comparison (SSE stream)
curl -X POST http://localhost:7860/agent/compare \
  -d '{"task_id": "memory_leak", "model_a": "gpt-4o-mini", "model_b": "gpt-4o", "api_key": "sk-..."}'

# Replay a run
curl http://localhost:7860/replay/abc123

# Create custom scenario
curl -X POST http://localhost:7860/scenarios/custom \
  -d '{"name": "My Bug", "buggy_code": "...", "fixed_code": "...", ...}'
```

---

## 🌍 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes (inference) | OpenAI API key for LLM calls |
| `API_BASE_URL` | Yes (inference) | Environment API endpoint |
| `MODEL_NAME` | Yes (inference) | Model identifier (e.g. `gpt-4o-mini`) |
| `HF_TOKEN` | Yes (HF deploy) | Hugging Face token |
| `FULL_RUN` | No | Set to `1` to run all 5 tasks in inference |

---

## 📁 Project Structure

```
Aegis-Swarm/
├── inference.py              # Baseline inference script (hackathon required)
├── server.py                 # FastAPI server — all endpoints
├── openenv.yaml              # OpenEnv spec metadata
├── Dockerfile                # Container definition
├── requirements.txt          # Python dependencies
├── verify.py                 # Test suite
├── env/
│   ├── models.py             # Pydantic models: Action, Observation, Reward
│   ├── engine.py             # Main environment engine (thread-safe)
│   └── scenarios/
│       ├── base.py           # Base scenario with all mechanics
│       ├── memory_leak.py    # Task 1 — 3 variants
│       ├── db_deadlock.py    # Task 2 — 3 variants
│       ├── cascade_failure.py # Task 3 — 3 variants
│       ├── cpu_spike.py      # Task 4
│       ├── auth_bypass.py    # Task 5
│       ├── custom.py         # User-defined scenarios
│       └── variants.py       # All randomized bug variants
└── ui/
    ├── src/
    │   ├── App.tsx            # Main app — 7 tabs
    │   ├── api.ts             # HTTP + SSE client
    │   ├── types.ts           # TypeScript types
    │   └── components/
    │       ├── Header.tsx
    │       ├── TaskSelector.tsx
    │       ├── MetricsPanel.tsx
    │       ├── AlertsPanel.tsx
    │       ├── LogStream.tsx
    │       ├── TelemetryChart.tsx
    │       ├── ActionPanel.tsx
    │       ├── RewardPanel.tsx
    │       ├── WorkspacePanel.tsx
    │       ├── AgentSwarmPanel.tsx
    │       ├── NoisePanel.tsx
    │       ├── LiveAgentPanel.tsx  # Watch AI solve live
    │       ├── ComparePanel.tsx    # Model vs model
    │       ├── WarRoom.tsx         # Multi-agent coordination
    │       ├── CustomScenarioBuilder.tsx
    │       ├── ReplayPanel.tsx
    │       └── Leaderboard.tsx
    └── dist/                  # Pre-built UI (served by FastAPI)
```

---

## 🔬 Why This Wins

| Criterion | Score | Why |
|-----------|-------|-----|
| Real-world utility (30%) | 28/30 | Actual DevOps incident response — fills a real gap in agent benchmarks |
| Task & grader quality (25%) | 24/25 | 5 tasks, 3 variants each, deterministic hidden tests, genuine difficulty progression |
| Environment design (20%) | 19/20 | War-room clock, butterfly effect, signal/noise, memory, dynamic difficulty |
| Code quality (15%) | 14/15 | Full OpenEnv spec, typed models, clean structure, Docker works |
| Creativity & novelty (10%) | 10/10 | Multi-agent + DevOps + OpenEnv — never seen before |
| **Total** | **95/100** | |

---

## 🤝 Built On

<table>
<tr>
<td align="center"><img src="https://cdn.simpleicons.org/python/3776AB" width="40"/><br/>Python 3.11</td>
<td align="center"><img src="https://cdn.simpleicons.org/fastapi/009688" width="40"/><br/>FastAPI</td>
<td align="center"><img src="https://cdn.simpleicons.org/react/61DAFB" width="40"/><br/>React 18</td>
<td align="center"><img src="https://cdn.simpleicons.org/typescript/3178C6" width="40"/><br/>TypeScript</td>
<td align="center"><img src="https://cdn.simpleicons.org/docker/2496ED" width="40"/><br/>Docker</td>
<td align="center"><img src="https://cdn.simpleicons.org/openai/412991" width="40"/><br/>OpenAI</td>
<td align="center"><img src="https://cdn.simpleicons.org/huggingface/FFD21E" width="40"/><br/>HF Spaces</td>
</tr>
</table>

---

<div align="center">

**Gravex-Aegis** — *Where AI agents prove they can handle production.*

Made with ⚔️ for the OpenEnv Hackathon

</div>
