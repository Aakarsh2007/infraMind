"""
InfraMind — Autonomous DevOps Benchmark
Complete FastAPI server — OpenEnv + all enterprise features.
"""
from __future__ import annotations
import asyncio, json, os, sys, time, threading
from typing import Any, Dict, List, Optional
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ValidationError

from env.engine import get_env, TASK_META, InfraMindEnv, AegisSwarmEnv
from env.models import Action, ActionType, AgentRole, FeedbackRequest, CustomScenarioRequest

app = FastAPI(
    title="InfraMind: Autonomous DevOps Benchmark",
    description="OpenEnv multi-agent SRE simulation. 5 tasks, seeded reproducibility, live AI agent, judge mode, episode trace export, adversarial agent, skill breakdown.",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Per-session environments for comparison mode ──────────────────────────────
_session_envs: Dict[str, InfraMindEnv] = {}
_session_lock = threading.Lock()

def get_session_env(session_id: str) -> InfraMindEnv:
    with _session_lock:
        if session_id not in _session_envs:
            _session_envs[session_id] = InfraMindEnv()
        return _session_envs[session_id]

# ── WebSocket ─────────────────────────────────────────────────────────────────
_ws_clients: List[WebSocket] = []

async def _broadcast(payload: dict):
    dead = []
    for ws in list(_ws_clients):
        try:
            await ws.send_text(json.dumps(payload, default=str))
        except:
            dead.append(ws)
    for ws in dead:
        if ws in _ws_clients: _ws_clients.remove(ws)

# ── Request models ────────────────────────────────────────────────────────────
class ResetRequest(BaseModel):
    task_id: Optional[str] = "memory_leak"
    model: Optional[str] = "unknown"
    seed: Optional[int] = None  # Explicit seed for reproducibility

class StepRequest(BaseModel):
    agent: str = "debugger"
    action_type: str
    command: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None
    patch_description: Optional[str] = None
    message: Optional[str] = None
    target_agent: Optional[str] = None
    service_name: Optional[str] = None
    reasoning: Optional[str] = None

# ── OpenEnv endpoints ─────────────────────────────────────────────────────────
@app.post("/reset", tags=["OpenEnv"], summary="Reset environment to a new episode")
async def reset(req: ResetRequest):
    try:
        obs = get_env().reset(task_id=req.task_id, model=req.model or "unknown", seed=req.seed)
        await _broadcast({"event": "reset", "task_id": req.task_id, "seed": obs.seed})
        return obs.model_dump()
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/step", tags=["OpenEnv"], summary="Execute one action")
async def step(req: StepRequest):
    try:
        action = Action(
            agent=AgentRole(req.agent),
            action_type=ActionType(req.action_type),
            command=req.command, file_path=req.file_path,
            content=req.content, patch_description=req.patch_description,
            message=req.message,
            target_agent=AgentRole(req.target_agent) if req.target_agent else None,
            service_name=req.service_name, reasoning=req.reasoning,
        )
    except (ValueError, ValidationError) as e:
        raise HTTPException(422, str(e))
    try:
        obs, reward, done, info = get_env().step(action)
        result = {"observation": obs.model_dump(), "reward": reward.model_dump(), "done": done, "info": info}
        await _broadcast({"event": "step", "step": obs.step, "done": done,
                          "metrics": obs.metrics.model_dump(),
                          "reward": reward.total if done else None,
                          "action_type": req.action_type, "agent": req.agent})
        return result
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/state", tags=["OpenEnv"], summary="Current episode state")
async def state():
    return get_env().state()


@app.get("/tasks", tags=["OpenEnv"], summary="List all tasks")
async def tasks():
    return {"tasks": get_env().tasks()}


# ── Analytics ─────────────────────────────────────────────────────────────────
@app.get("/leaderboard", tags=["Analytics"])
async def leaderboard():
    return {"leaderboard": get_env().leaderboard()}

@app.get("/history", tags=["Analytics"])
async def history():
    return {"history": get_env().history()}

@app.get("/stats", tags=["Analytics"])
async def stats():
    return get_env().stats()

@app.get("/memory", tags=["Analytics"], summary="Agent memory across episodes")
async def memory():
    return {"memory": get_env().memory()}

@app.get("/feedback/summary", tags=["Analytics"])
async def feedback_summary():
    return get_env().feedback_summary()


# ── Feedback & Learning ───────────────────────────────────────────────────────
@app.post("/feedback", tags=["Learning"], summary="Submit feedback on a completed run")
async def submit_feedback(req: FeedbackRequest):
    return get_env().submit_feedback(req)


# ── Custom Scenarios ──────────────────────────────────────────────────────────
@app.post("/scenarios/custom", tags=["Custom"], summary="Add a custom scenario")
async def add_custom_scenario(req: CustomScenarioRequest):
    return get_env().add_custom_scenario(req)

@app.get("/scenarios/custom", tags=["Custom"], summary="List custom scenarios")
async def list_custom_scenarios():
    return {"custom_scenarios": list(get_env()._custom_scenarios.keys())}


# ── System ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "infra-mind", "version": "5.0.0",
            "tasks": len(TASK_META), "timestamp": time.time()}

@app.get("/openenv.yaml", tags=["System"], response_class=HTMLResponse)
async def openenv_yaml():
    try:
        with open(os.path.join(os.path.dirname(__file__), "openenv.yaml")) as f:
            return HTMLResponse(f.read(), media_type="text/yaml")
    except:
        raise HTTPException(404, "openenv.yaml not found")


# ── Judge Mode ────────────────────────────────────────────────────────────────
class JudgeRequest(BaseModel):
    seed: int = 42

@app.post("/judge/run_all", tags=["Judge"], summary="One-click evaluation across all tasks — for judges")
async def judge_run_all(req: JudgeRequest):
    """
    Runs a deterministic baseline evaluation across all 5 tasks.
    Returns avg score, per-task scores, skill diagnostics.
    Perfect for judges who want instant testability.
    """
    try:
        result = get_env().judge_run_all(seed=req.seed)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Episode Trace Export ──────────────────────────────────────────────────────
@app.get("/export/{run_id}", tags=["Analytics"], summary="Export full episode trace for RL training / research")
async def export_trace(run_id: str):
    """
    Returns complete episode trace: all steps, actions, metrics, rewards.
    Usable for RL training datasets and research papers.
    """
    trace = get_env().export_trace(run_id)
    if trace is None:
        raise HTTPException(404, f"Run {run_id} not found")
    return trace.model_dump()


# ── Skill Breakdown ───────────────────────────────────────────────────────────
@app.get("/skills/{run_id}", tags=["Analytics"], summary="Get skill breakdown for a completed run")
async def skill_breakdown(run_id: str):
    """Returns per-skill scores: root_cause_accuracy, debugging_efficiency, patch_quality, collaboration, noise_filtering, speed."""
    for rec in get_env()._run_history:
        if rec.run_id == run_id:
            return {
                "run_id": run_id,
                "skill_breakdown": rec.skill_breakdown.model_dump() if rec.skill_breakdown else {},
                "failure_report": rec.failure_report.model_dump() if rec.failure_report else {},
            }
    raise HTTPException(404, f"Run {run_id} not found")


# ── Live AI Agent (SSE streaming) ─────────────────────────────────────────────
class AgentRunRequest(BaseModel):
    task_id: str = "memory_leak"
    api_key: str
    model: str = "gpt-4o-mini"
    max_steps: int = 20

@app.post("/agent/run", tags=["Live Agent"], summary="Run AI agent live — streams via SSE")
async def agent_run(req: AgentRunRequest):
    async def stream():
        try:
            from openai import OpenAI as _OAI
            client = _OAI(api_key=req.api_key)
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"; return

        env = get_env()
        try:
            obs = env.reset(task_id=req.task_id, model=req.model)
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"; return

        yield f"data: {json.dumps({'type':'reset','task_id':req.task_id,'model':req.model,'observation':obs.model_dump()}, default=str)}\n\n"

        SYSTEM = """You are an elite SRE AI. Diagnose and fix the production incident.
Respond ONLY with JSON (no markdown):
{"agent":"debugger|coder|coordinator","action_type":"terminal|read_file|edit_file|list_files|search_logs|submit_patch","command":"...","file_path":"...","content":"...","patch_description":"...","reasoning":"one sentence why"}
Strategy: list_files → search_logs ERROR → read_file → edit_file → submit_patch. Be efficient."""

        history = []
        done = False
        step = 0

        while not done and step < req.max_steps:
            step += 1
            m = obs.metrics
            parts = [f"STEP={obs.step} TASK={obs.task_id} PRESSURE={obs.time_pressure}",
                     f"CPU={m.cpu_percent}% MEM={m.memory_percent}% ERR={m.error_rate*100:.1f}%"]
            if obs.active_alerts:
                parts.append("ALERTS: " + " | ".join(f"[{a.severity}] {a.service}: {a.message}" for a in obs.active_alerts[:2]))
            if obs.recent_logs:
                parts.append("LOGS:\n" + "\n".join(obs.recent_logs[-8:]))
            if obs.available_files:
                parts.append("FILES: " + ", ".join(obs.available_files))
            if obs.action_result:
                parts.append("RESULT:\n" + obs.action_result[:800])
            if obs.memory_hints:
                parts.append("MEMORY: " + " | ".join(obs.memory_hints))

            history.append({"role": "user", "content": "\n".join(parts)})
            try:
                resp = client.chat.completions.create(
                    model=req.model,
                    messages=[{"role":"system","content":SYSTEM}]+history[-14:],
                    temperature=0.1, max_tokens=500)
                raw = (resp.choices[0].message.content or "{}").strip()
                history.append({"role":"assistant","content":raw})
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"): raw = raw[4:]
                action_dict = json.loads(raw.strip())
            except Exception as e:
                action_dict = {"agent":"debugger","action_type":"search_logs","command":"ERROR","reasoning":f"parse error: {e}"}

            try:
                action = Action(
                    agent=AgentRole(action_dict.get("agent","debugger")),
                    action_type=ActionType(action_dict.get("action_type","search_logs")),
                    command=action_dict.get("command"), file_path=action_dict.get("file_path"),
                    content=action_dict.get("content"), patch_description=action_dict.get("patch_description"),
                    reasoning=action_dict.get("reasoning"))
                obs, reward, done, info = env.step(action)
            except Exception as e:
                yield f"data: {json.dumps({'type':'error','step':step,'message':str(e)})}\n\n"; break

            yield f"data: {json.dumps({'type':'step','step':step,'agent':action_dict.get('agent'),'action_type':action_dict.get('action_type'),'reasoning':action_dict.get('reasoning',''),'action_result':obs.action_result,'metrics':obs.metrics.model_dump(),'logs':obs.recent_logs[-5:],'alerts':[a.model_dump() for a in obs.active_alerts],'done':done,'reward':reward.model_dump() if done else None}, default=str)}\n\n"
            await asyncio.sleep(0.05)

        yield f"data: {json.dumps({'type':'complete','steps':step,'done':done})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


# ── Comparison Mode ───────────────────────────────────────────────────────────
class CompareRequest(BaseModel):
    task_id: str = "memory_leak"
    model_a: str = "gpt-4o-mini"
    model_b: str = "gpt-4o"
    api_key: str
    max_steps: int = 15

@app.post("/agent/compare", tags=["Live Agent"], summary="Run two models on same task simultaneously")
async def agent_compare(req: CompareRequest):
    async def stream():
        try:
            from openai import OpenAI as _OAI
            client = _OAI(api_key=req.api_key)
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"; return

        env_a = AegisSwarmEnv()
        env_b = AegisSwarmEnv()
        obs_a = env_a.reset(task_id=req.task_id, model=req.model_a)
        obs_b = env_b.reset(task_id=req.task_id, model=req.model_b)

        yield f"data: {json.dumps({'type':'compare_start','task_id':req.task_id,'model_a':req.model_a,'model_b':req.model_b})}\n\n"

        SYSTEM = """SRE AI. JSON only: {"agent":"debugger|coder","action_type":"terminal|read_file|edit_file|list_files|search_logs|submit_patch","command":"...","file_path":"...","content":"...","patch_description":"...","reasoning":"..."}"""
        hist_a, hist_b = [], []
        done_a = done_b = False
        reward_a = reward_b = 0.0
        steps_a = steps_b = 0

        for step in range(req.max_steps):
            if done_a and done_b: break
            for side, env, obs, hist, model, done_flag in [
                ("a", env_a, obs_a, hist_a, req.model_a, done_a),
                ("b", env_b, obs_b, hist_b, req.model_b, done_b),
            ]:
                if done_flag: continue
                m = obs.metrics
                prompt = f"STEP={obs.step} CPU={m.cpu_percent}% MEM={m.memory_percent}% ERR={m.error_rate*100:.1f}%\nLOGS:\n" + "\n".join(obs.recent_logs[-6:]) + f"\nFILES: {', '.join(obs.available_files)}" + (f"\nRESULT:\n{obs.action_result[:400]}" if obs.action_result else "")
                hist.append({"role":"user","content":prompt})
                try:
                    resp = client.chat.completions.create(model=model, messages=[{"role":"system","content":SYSTEM}]+hist[-10:], temperature=0.1, max_tokens=400)
                    raw = (resp.choices[0].message.content or "{}").strip()
                    hist.append({"role":"assistant","content":raw})
                    if raw.startswith("```"):
                        raw = raw.split("```")[1]
                        if raw.startswith("json"): raw = raw[4:]
                    ad = json.loads(raw.strip())
                except Exception:
                    ad = {"agent":"debugger","action_type":"search_logs","command":"ERROR"}
                try:
                    action = Action(agent=AgentRole(ad.get("agent","debugger")), action_type=ActionType(ad.get("action_type","search_logs")), command=ad.get("command"), file_path=ad.get("file_path"), content=ad.get("content"), patch_description=ad.get("patch_description"), reasoning=ad.get("reasoning"))
                    new_obs, rew, done, _ = env.step(action)
                except Exception as e:
                    yield f"data: {json.dumps({'type':'error','side':side,'message':str(e)})}\n\n"; continue
                if side == "a":
                    obs_a = new_obs; done_a = done
                    if done: reward_a = rew.total; steps_a = step+1
                else:
                    obs_b = new_obs; done_b = done
                    if done: reward_b = rew.total; steps_b = step+1
                yield f"data: {json.dumps({'type':'compare_step','side':side,'step':step+1,'model':model,'action_type':ad.get('action_type'),'reasoning':ad.get('reasoning',''),'metrics':new_obs.metrics.model_dump(),'done':done,'reward':rew.total if done else None}, default=str)}\n\n"
                await asyncio.sleep(0.05)

        winner = req.model_a if reward_a >= reward_b else req.model_b
        yield f"data: {json.dumps({'type':'compare_complete','model_a':req.model_a,'reward_a':reward_a,'steps_a':steps_a,'model_b':req.model_b,'reward_b':reward_b,'steps_b':steps_b,'winner':winner})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


# ── Replay ────────────────────────────────────────────────────────────────────
@app.get("/replay/{run_id}", tags=["Analytics"], summary="Get replay data for a completed run")
async def replay(run_id: str):
    for rec in get_env()._run_history:
        if rec.run_id == run_id:
            return rec.to_dict()
    raise HTTPException(404, f"Run {run_id} not found")


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    _ws_clients.append(ws)
    try:
        await ws.send_text(json.dumps({"event": "connected", "state": get_env().state()}, default=str))
        while True:
            await asyncio.sleep(3)
            s = get_env().state()
            if s.get("current_metrics"):
                await ws.send_text(json.dumps({"event": "heartbeat", "state": s}, default=str))
    except WebSocketDisconnect:
        pass
    finally:
        if ws in _ws_clients: _ws_clients.remove(ws)


# ── UI ────────────────────────────────────────────────────────────────────────
_ui_dir = os.path.join(os.path.dirname(__file__), "ui", "dist")
_API_PREFIXES = ("reset","step","state","tasks","leaderboard","history","stats",
                 "memory","feedback","scenarios","health","openenv","ws","docs","redoc","openapi",
                 "agent","replay","session","judge","export","skills")

if os.path.isdir(_ui_dir):
    _assets = os.path.join(_ui_dir, "assets")
    if os.path.isdir(_assets):
        app.mount("/assets", StaticFiles(directory=_assets), name="assets")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def serve_ui(full_path: str = ""):
        if any(full_path.startswith(p) for p in _API_PREFIXES):
            raise HTTPException(404)
        with open(os.path.join(_ui_dir, "index.html")) as f:
            return HTMLResponse(f.read())
else:
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def serve_fallback():
        return HTMLResponse(_FALLBACK)

_FALLBACK = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<title>Gravex-Aegis</title>
<style>*{box-sizing:border-box;margin:0;padding:0}body{background:#080c18;color:#e2e8f0;font-family:'Segoe UI',system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:2rem}.wrap{text-align:center;max-width:700px}h1{font-size:3rem;font-weight:900;background:linear-gradient(135deg,#f97316,#ef4444,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.5rem}p{color:#64748b;margin-bottom:2rem}.links{display:flex;gap:.75rem;justify-content:center;flex-wrap:wrap}a{padding:.6rem 1.5rem;border-radius:.5rem;text-decoration:none;font-weight:600;font-size:.9rem;background:#1d4ed8;color:#fff}</style>
</head><body><div class="wrap"><h1>⚔️ Gravex-Aegis</h1><p>Autonomous DevOps War-Room — OpenEnv Multi-Agent Environment</p>
<div class="links"><a href="/docs">📖 API Docs</a><a href="/tasks" style="background:#1f2937">📋 Tasks</a><a href="/leaderboard" style="background:#1f2937">🏆 Board</a><a href="/stats" style="background:#1f2937">📊 Stats</a></div></div></body></html>"""
