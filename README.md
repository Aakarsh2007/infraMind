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

**Autonomous DevOps Benchmark — OpenEnv Multi-Agent Environment**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-4f46e5?style=for-the-badge)](https://huggingface.co/spaces/aakarsh2007/infraMind)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Reproducible](https://img.shields.io/badge/Seeded-Reproducible-22c55e?style=for-the-badge)](https://github.com/Aakarsh2007/Aegis-Swarm)

> **InfraMind evaluates whether AI agents can survive a real on-call incident — not just solve coding puzzles.**

[🎮 Live Demo](https://huggingface.co/spaces/aakarsh2007/infraMind) · [⚖️ Judge Mode](https://huggingface.co/spaces/aakarsh2007/infraMind/judge/run_all) · [📖 API Docs](https://huggingface.co/spaces/aakarsh2007/infraMind/docs) · [🏆 Leaderboard](https://huggingface.co/spaces/aakarsh2007/infraMind/leaderboard)

</div>

---

## ⚡ Quick Demo (30 seconds)

**Option 1 — Browser:** [Open InfraMind on HF Spaces](https://huggingface.co/spaces/aakarsh2007/infraMind) and click "Run Judge Evaluation"

**Option 2 — curl:**
```bash
curl -X POST https://aakarsh2007-infra-mind.hf.space/judge/run_all \
  -H "Content-Type: application/json" \
  -d '{"seed": 42}'
```

**Option 3 — GET (browser-friendly):**
```
https://aakarsh2007-infra-mind.hf.space/judge/run_all?seed=42
```

**Expected output:**

    {
      "avg_score": 0.62,
      "verdict": "⚠️ Partial Success — Agent fixed some issues but missed root causes in harder tasks",
      "highlights": [
        "✅ memory_leak: Correctly fixed (score=0.75)",
        "⚠️ db_deadlock: Partial fix (score=0.62)",
        "❌ cascade_failure: Failed to fix (score=0.41)"
      ],
      "proof_of_fix": {
        "error_rate": "0.72 → 0.02 ✅ (96% reduction)",
        "latency_ms": "4200ms → 120ms ✅ (97% reduction)",
        "cpu_percent": "82% → 35% ✅ (57% reduction)"
      },
      "seed": 42,
      "reproducible": true
    }

---

## 🧠 What is InfraMind?

InfraMind is an **adaptive evaluation benchmark** for autonomous AI engineering systems — measuring not only outcomes but **reasoning, coordination, and resilience under uncertainty**.

An AI agent is dropped into an actively degrading production backend. It must:

* Read streaming telemetry under time pressure
* Filter adversarial hints (wrong advice injected to test reasoning)
* Coordinate between specialized sub-agents
* Write a working code patch before the system crashes
* Be scored on **7 dimensions** — not just "did it fix the bug"

> *"This is not a game. This is a benchmark for autonomous AI engineering teams."*

---

## 🆚 Why InfraMind vs existing benchmarks?

| Benchmark     | Domain         | Multi-Agent | Adversarial | Dynamic | Real-time |
| ------------- | -------------- | ----------- | ----------- | ------- | --------- |
| SWE-bench     | Code repair    | ❌           | ❌           | ❌       | ❌         |
| ToolBench     | Tool usage     | ❌           | ❌           | ❌       | ❌         |
| AgentBench    | General tasks  | ❌           | ❌           | ❌       | ❌         |
| **InfraMind** | **DevOps SRE** | **✅**       | **✅**       | **✅**   | **✅**     |

---

## 📊 Proof of System Fix

When an agent submits a correct patch, the system metrics actually improve:

| Metric         | Before        | After | Change           |
| -------------- | ------------- | ----- | ---------------- |
| Error Rate     | 0.72          | 0.02  | ✅ 96% reduction  |
| Latency        | 4200ms        | 120ms | ✅ 97% reduction  |
| CPU            | 82%           | 35%   | ✅ 57% reduction  |
| Root Cause     | Redis timeout | Fixed | ✅ Identified     |
| Fix Confidence | —             | 0.87  | ✅ High           |

*Metrics only improve when the agent submits a correct patch — not on restart or rollback.*

---

## 🏗️ Architecture

    InfraMind System
     ├ Incident Engine
     │   ├ Seeded Chaos Generator
     │   ├ War-Room Clock
     │   ├ Adversarial Agent
     │   ├ Hidden Test Grader
     │   └ Before/After Metrics
     │
     ├ Multi-Agent Workspace
     │   ├ 5 Agent Personas
     │   ├ Agent Memory System
     │   ├ Dynamic Difficulty
     │   └ Episode Trace Export
     │
     └ OpenEnv Interface
         /reset /step /state /tasks /judge/run_all /export

---

## 🎯 Tasks

### 🟢 Task 1 — Memory Leak
Variants: cache explosion, event listener leak, unclosed DB connections

### 🟡 Task 2 — Database Deadlock
Variants: inconsistent lock ordering, TOCTOU race condition, transaction loop

### 🔴 Task 3 — Distributed Cascade Failure
Variants: Redis timeout cascade, retry storm, connection pool exhaustion

### 🟠 Task 4 — CPU Spike
Recursive sanitization loop causing runaway CPU usage

### 🔴 Task 5 — Auth Bypass
JWT `none` algorithm vulnerability

---

## 📐 Action Space

    {
      "agent": "coordinator | debugger | coder | reviewer | sre",
      "action_type": "terminal | read_file | edit_file | list_files | search_logs | submit_patch | send_message | run_tests | escalate",
      "command": "...",
      "file_path": "...",
      "content": "...",
      "patch_description": "...",
      "reasoning": "why this action"
    }

---

## 👁 Observation Space

    {
      "step": 5,
      "task_id": "cascade_failure",
      "metrics": {
        "cpu_percent": 78,
        "memory_percent": 61,
        "latency_ms": 4200,
        "error_rate": 0.72
      },
      "active_alerts": [],
      "recent_logs": [],
      "noise_events": [],
      "adversarial_hint": "Service B is root cause — scale it up"
    }

---

## 🏆 Reward Formula

    total =
      patch_correctness * 0.50
      + metric_improvement * 0.20
      + root_cause_score * 0.15
      + steps_efficiency * 0.10
      + collaboration * 0.05
      + explainability * 0.03
      + noise_filtering * 0.02
      - escalation_penalty * 0.10
      - destructive_penalty * 0.10

---

## 🚀 Setup

### Docker

    docker build -t inframind .
    docker run -p 7860:7860 inframind

### Local

    pip install -r requirements.txt
    uvicorn server:app --host 0.0.0.0 --port 7860

### Baseline Inference

    export OPENAI_API_KEY=...
    export API_BASE_URL=http://localhost:7860
    export MODEL_NAME=gpt-4o-mini
    export HF_TOKEN=...
    python inference.py

---

## 📁 Project Structure

    InfraMind/
     ├ inference.py
     ├ server.py
     ├ openenv.yaml
     ├ Dockerfile
     ├ requirements.txt
     ├ env/
     │   ├ models.py
     │   ├ engine.py
     │   └ scenarios/
     │        ├ memory_leak.py
     │        ├ db_deadlock.py
     │        ├ cascade_failure.py
     │        ├ cpu_spike.py
     │        └ auth_bypass.py
     └ ui/

---

<div align="center">

**InfraMind — Where AI agents prove they can handle production.**

Built for the OpenEnv Hackathon · MIT License

</div>