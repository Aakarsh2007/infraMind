"""
Task 5 — Auth Bypass / Security Incident (Hard)
A JWT verification function has a critical vulnerability: it accepts
the 'none' algorithm, allowing attackers to forge tokens. The Aegis
probe detected anomalous 200 responses on admin endpoints from
unauthenticated IPs. The agent must find and patch the security bug.
"""
from __future__ import annotations
import time
from typing import Dict, List, Optional
from env.models import Action, Alert, AlertSeverity, NoiseEvent, Reward, SystemMetrics
from env.scenarios.base import BaseScenario

BUGGY_AUTH = """\
// middleware/auth.js — JWT authentication middleware
const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET || 'supersecret';

// CRITICAL VULNERABILITY: accepts 'none' algorithm — allows token forgery
function verifyToken(token) {
  try {
    // BUG: No algorithm whitelist — attacker can set alg:'none' and skip signature
    const decoded = jwt.verify(token, SECRET);
    return { valid: true, payload: decoded };
  } catch (err) {
    return { valid: false, error: err.message };
  }
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return res.status(401).json({ error: 'No token' });
  const token = authHeader.split(' ')[1];
  const result = verifyToken(token);
  if (!result.valid) return res.status(403).json({ error: result.error });
  req.user = result.payload;
  next();
}

module.exports = { authMiddleware, verifyToken };
"""

FIXED_AUTH = """\
// middleware/auth.js — JWT authentication middleware (FIXED)
const jwt = require('jsonwebtoken');
const SECRET = process.env.JWT_SECRET;

if (!SECRET) throw new Error('JWT_SECRET environment variable is required');

// FIX: Whitelist only HS256 — reject 'none' and other weak algorithms
const ALLOWED_ALGORITHMS = ['HS256'];

function verifyToken(token) {
  if (!token || typeof token !== 'string') return { valid: false, error: 'Invalid token format' };
  try {
    const decoded = jwt.verify(token, SECRET, {
      algorithms: ALLOWED_ALGORITHMS, // Explicit whitelist — blocks 'none' attack
    });
    return { valid: true, payload: decoded };
  } catch (err) {
    return { valid: false, error: err.message };
  }
}

function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header' });
  }
  const token = authHeader.split(' ')[1];
  const result = verifyToken(token);
  if (!result.valid) return res.status(403).json({ error: result.error });
  req.user = result.payload;
  next();
}

module.exports = { authMiddleware, verifyToken };
"""

HIDDEN_TESTS = [
    ("Algorithm whitelist present", lambda c: "algorithms" in c and ("HS256" in c or "RS256" in c)),
    ("'none' algorithm blocked", lambda c: "algorithms" in c or "whitelist" in c.lower()),
    ("JWT_SECRET required check", lambda c: "JWT_SECRET" in c and ("throw" in c or "Error" in c or "required" in c.lower())),
    ("Bearer prefix validated", lambda c: "Bearer" in c or "startsWith" in c),
    ("Returns 403 on invalid", lambda c: "403" in c or "status(403)" in c),
]


class AuthBypassScenario(BaseScenario):
    task_id = "auth_bypass"
    max_steps = 30

    NOISE_SCHEDULE = {
        3: [NoiseEvent(source="support_ticket", content="Users getting logged out randomly — is auth broken?")],
        7: [NoiseEvent(source="slack_alert", content="Security scanner: 'High severity finding in auth module'")],
        12: [NoiseEvent(source="twitter", content="Reports of account takeovers on your platform #security")],
        18: [NoiseEvent(source="email", content="Legal: 'We need a security incident report by EOD'")],
    }

    def initial_files(self) -> Dict[str, str]:
        return {
            "middleware/auth.js": BUGGY_AUTH,
            "routes/admin.js": "const { authMiddleware } = require('../middleware/auth');\nconst express = require('express');\nconst router = express.Router();\nrouter.use(authMiddleware);\nrouter.get('/users', (req,res) => res.json({users: [], requestedBy: req.user}));\nrouter.delete('/user/:id', (req,res) => res.json({deleted: req.params.id}));\nmodule.exports = router;",
            "routes/public.js": "const express = require('express');\nconst router = express.Router();\nrouter.get('/health', (req,res) => res.json({status:'ok'}));\nmodule.exports = router;",
            "server.js": "const express = require('express');\nconst admin = require('./routes/admin');\nconst pub = require('./routes/public');\nconst app = express();\napp.use(express.json());\napp.use('/admin', admin);\napp.use('/', pub);\napp.listen(3000);\n",
            "package.json": '{"name":"api-service","version":"3.0.0","dependencies":{"express":"^4.18.0","jsonwebtoken":"^9.0.0"}}',
        }

    def initial_logs(self) -> List[str]:
        return [
            "[2026-04-05T22:00:00Z] INFO  api-service started",
            "[2026-04-05T22:01:00Z] INFO  GET /admin/users 200 — user: admin@company.com",
            "[2026-04-05T22:15:00Z] WARN  GET /admin/users 200 — user: {role:'admin',alg:'none'} from IP 185.220.101.45",
            "[2026-04-05T22:15:01Z] WARN  DELETE /admin/user/1001 200 — user: {role:'admin',alg:'none'} from IP 185.220.101.45",
            "[2026-04-05T22:15:02Z] WARN  DELETE /admin/user/1002 200 — user: {role:'admin',alg:'none'} from IP 185.220.101.45",
            "[2026-04-05T22:15:10Z] ERROR SECURITY: 47 admin actions from unauthenticated IP in 10 seconds",
            "[2026-04-05T22:15:11Z] ERROR JWT alg:'none' accepted — signature verification bypassed",
            "[2026-04-05T22:15:12Z] CRITICAL BREACH: admin endpoint accessed without valid signature",
        ]

    def initial_alerts(self) -> List[Alert]:
        return [
            Alert(id="e1", severity=AlertSeverity.CRITICAL, service="api-service",
                  message="SECURITY BREACH: JWT 'none' algorithm accepted — admin endpoints compromised",
                  timestamp=time.time()),
            Alert(id="e2", severity=AlertSeverity.CRITICAL, service="api-service",
                  message="47 unauthorized admin actions from IP 185.220.101.45", timestamp=time.time()),
        ]

    def initial_metrics(self) -> SystemMetrics:
        return SystemMetrics(cpu_percent=35.0, memory_percent=42.0, latency_ms=45.0,
                             error_rate=0.0, active_connections=88, uptime_seconds=86400.0)

    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics:
        prev = self._metrics_history[-1]
        # Security incident — metrics look normal (that's the trick)
        attack_rate = min(200, step * 15)
        self._log_buffer.append(
            f"[SECURITY] step={step} unauthorized_requests={attack_rate} from 185.220.101.45"
        )
        return SystemMetrics(cpu_percent=round(prev.cpu_percent + 0.5, 1),
                             memory_percent=round(prev.memory_percent, 1),
                             latency_ms=round(prev.latency_ms, 1), error_rate=0.0,
                             active_connections=prev.active_connections,
                             uptime_seconds=prev.uptime_seconds + 30)

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        code = self._files.get("middleware/auth.js", patch_content)
        passed = sum(1 for _, fn in HIDDEN_TESTS if fn(code))
        fraction = passed / len(HIDDEN_TESTS)
        steps_bonus = max(0.0, (self.max_steps - self.step_count) / self.max_steps) * 0.2
        desc_lower = (patch_description or "").lower()
        root = 1.0 if ("none" in desc_lower or "algorithm" in desc_lower or "jwt" in desc_lower) else 0.3
        total = min(1.0, fraction * 0.65 + steps_bonus + root * 0.15)
        return Reward(total=round(total, 3), patch_correctness=round(fraction, 3),
                      hidden_tests_passed=round(fraction, 3), steps_efficiency=round(steps_bonus / 0.2, 3),
                      root_cause_identified=root, no_regression=1.0 if "403" in code else 0.5,
                      reason=f"Passed {passed}/{len(HIDDEN_TESTS)} security tests.",
                      post_mortem={"root_cause": "JWT verifyToken() accepts 'none' algorithm — no whitelist",
                                   "cve_class": "CWE-347: Improper Verification of Cryptographic Signature",
                                   "agent_steps": self.step_count, "optimal_steps": 8,
                                   "hidden_tests": {d: fn(code) for d, fn in HIDDEN_TESTS}})

    def escalation_hint(self) -> str:
        return "The vulnerability is in middleware/auth.js. jwt.verify() without an algorithms whitelist accepts alg:'none', bypassing signature verification. Fix: pass {algorithms: ['HS256']} as the third argument to jwt.verify()."
