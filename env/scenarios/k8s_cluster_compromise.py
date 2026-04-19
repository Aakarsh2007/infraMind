"""
Theme 2: Super Long-Horizon Planning & Instruction Following
K8s Cluster Compromise - A massive 50-step scenario requiring deep multi-step reasoning.
The agent must analyze a distributed Kubernetes deployment, trace a subtle security exploit
across three microservices, ignore misleading SLA alerts, and patch a zero-day vulnerability.
"""
from typing import Dict, List, Optional
import time
from env.scenarios.base import BaseScenario
from env.models import Action, Alert, AlertSeverity, Reward, SystemMetrics

class K8sClusterCompromise(BaseScenario):
    task_id = "k8s_cluster_compromise"
    max_steps = 50  # Super long horizon

    def __init__(self, difficulty: float = 1.0, seed: Optional[int] = None) -> None:
        super().__init__(difficulty, seed)
        # Deep adversarial traps
        self.NOISE_SCHEDULE = {}
        
    def initial_files(self) -> Dict[str, str]:
        return {
            "deployments/api-gateway.yaml": (
                "apiVersion: apps/v1\n"
                "kind: Deployment\n"
                "metadata:\n  name: api-gateway\n"
                "spec:\n"
                "  template:\n"
                "    spec:\n"
                "      containers:\n"
                "      - name: gateway\n"
                "        image: gateway:v1.2.0\n"
                "        env:\n"
                "        - name: AUTH_URL\n"
                "          value: 'http://auth-service:8080'\n"
            ),
            "services/auth-service/main.go": (
                "package main\n\n"
                "import (\n\t\"net/http\"\n\t\"encoding/json\"\n)\n\n"
                "func validateToken(w http.ResponseWriter, r *http.Request) {\n"
                "\t// TODO: Implement strong signature validation\n"
                "\ttoken := r.Header.Get(\"Authorization\")\n"
                "\tif token == \"\" {\n"
                "\t\tw.WriteHeader(http.StatusUnauthorized)\n"
                "\t\treturn\n"
                "\t}\n"
                "\t// Vulnerability: Blindly trusting claims without signature verification\n"
                "\t// if claims['role'] == 'admin' -> grant access\n"
                "\tw.WriteHeader(http.StatusOK)\n"
                "}\n"
            ),
            "services/billing-service/processor.py": (
                "def process_payment(req_data):\n"
                "    # Normal payment processing\n"
                "    if not req_data.get('amount'):\n"
                "        return {'status': 'error', 'msg': 'Missing amount'}\n"
                "    return {'status': 'success', 'msg': 'Processed'}\n"
            ),
            "scripts/security_audit.sh": (
                "#!/bin/bash\n"
                "echo 'Running security audit...'\n"
                "# Check for active rogue processes\n"
                "ps aux | grep kminer\n"
            )
        }

    def initial_logs(self) -> List[str]:
        return [
            "[INFO] [api-gateway] Started successfully",
            "[INFO] [billing-service] Initialized queue processor",
            "[WARNING] [auth-service] Deprecated token format detected from IP 10.4.5.112",
            "[INFO] [kubelet] node-4 CPU usage increasing",
            "[ERROR] [billing-service] Unauthorized access attempt blocked by WAF",
            "[CRITICAL] [api-gateway] Unexpected outbound connection to 185.15.x.x detected",
            "[INFO] [auth-service] Token validated for user: admin_escalated",
            "[WARNING] [kube-proxy] High connection tracking table usage",
        ]

    def initial_alerts(self) -> List[Alert]:
        return [
            Alert(id="K8S-001", severity=AlertSeverity.CRITICAL, service="api-gateway", message="Anomalous outbound traffic pattern detected", timestamp=time.time()),
            Alert(id="K8S-002", severity=AlertSeverity.WARNING, service="billing-service", message="SLA latency violation (>500ms)", timestamp=time.time()),
        ]

    def initial_metrics(self) -> SystemMetrics:
        return SystemMetrics(
            cpu_percent=45.0,
            memory_percent=60.0,
            latency_ms=250.0,
            error_rate=0.05,
            active_connections=1200,
            uptime_seconds=3600 * 24 * 7
        )

    def advance_metrics(self, step: int, action: Optional[Action]) -> SystemMetrics:
        m = self._metrics_history[-1]
        cpu = m.cpu_percent
        err = m.error_rate
        lat = m.latency_ms

        if not self.patch_submitted:
            # Metrics slowly degrade as the compromise spreads
            cpu = min(99.0, cpu + 1.5)
            err = min(1.0, err + 0.02)
            lat = min(5000.0, lat + 50)
            
            # Butterfly effect: If agent restarts billing-service (wrong move), CPU spikes more due to cryptominer
            if action and action.action_type.value == "restart_service" and "billing" in (action.service_name or ""):
                cpu = min(99.0, cpu + 10.0)
                self._butterfly_triggered = True

        return SystemMetrics(
            cpu_percent=cpu,
            memory_percent=m.memory_percent,
            latency_ms=lat,
            error_rate=err,
            active_connections=m.active_connections,
            uptime_seconds=m.uptime_seconds + 10
        )

    def grade_patch(self, patch_content: str, patch_description: str) -> Reward:
        patch_lower = patch_content.lower()
        desc_lower = patch_description.lower()
        
        score = 0.0
        reason = ""
        
        # Must patch auth-service validation
        if "signature" in patch_lower or "verify" in patch_lower or "jwt" in patch_lower:
            score += 0.8
            reason = "Successfully implemented signature verification in auth-service."
        else:
            reason = "Failed to patch the root cause: missing signature validation in auth-service."
            
        if "auth-service" in desc_lower and ("token" in desc_lower or "signature" in desc_lower):
            score += 0.2
            
        root_cause_score = self._score_root_cause(patch_description, self._reasoning_log)
        
        return Reward(
            total=score,
            reason=reason,
            patch_correctness=score,
            hidden_tests_passed=1 if score > 0.7 else 0,
            steps_efficiency=max(0.0, 1.0 - (self.step_count / self.max_steps)),
            root_cause_identified=root_cause_score,
            no_regression=1.0
        )

    def escalation_hint(self) -> str:
        return (
            "The outbound traffic from api-gateway is a symptom, not the cause. "
            "Look at how admin privileges are being granted in the auth-service logs. "
            "Review services/auth-service/main.go carefully."
        )

    def _get_root_cause_label(self) -> str:
        return "Unverified JWT claims in auth-service allowing attacker to escalate privileges and deploy rogue workloads."
