"""
InfraMind — OpenEnv typed models.
Action, Observation, Reward — fully typed Pydantic v2.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    TERMINAL = "terminal"
    READ_FILE = "read_file"
    EDIT_FILE = "edit_file"
    SUBMIT_PATCH = "submit_patch"
    ESCALATE = "escalate"
    LIST_FILES = "list_files"
    SEARCH_LOGS = "search_logs"
    SEND_MESSAGE = "send_message"
    CREATE_JIRA = "create_jira"
    COMMENT_PR = "comment_pr"
    RUN_TESTS = "run_tests"
    ROLLBACK = "rollback"
    RESTART_SERVICE = "restart_service"


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    DEBUGGER = "debugger"
    CODER = "coder"
    REVIEWER = "reviewer"
    SRE = "sre"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Action(BaseModel):
    agent: AgentRole = Field(..., description="Which agent persona is acting")
    action_type: ActionType = Field(..., description="Type of action")
    command: Optional[str] = Field(None, description="Shell command or search pattern")
    file_path: Optional[str] = Field(None, description="Target file path")
    content: Optional[str] = Field(None, description="New file content for EDIT_FILE")
    patch_description: Optional[str] = Field(None, description="Fix description for SUBMIT_PATCH")
    message: Optional[str] = Field(None, description="Message for SEND_MESSAGE / COMMENT_PR")
    target_agent: Optional[AgentRole] = Field(None, description="Target agent for SEND_MESSAGE")
    service_name: Optional[str] = Field(None, description="Service name for RESTART_SERVICE")
    reasoning: Optional[str] = Field(None, description="Agent's reasoning (for explainability score)")


class SystemMetrics(BaseModel):
    cpu_percent: float = Field(..., ge=0.0, le=100.0)
    memory_percent: float = Field(..., ge=0.0, le=100.0)
    latency_ms: float = Field(..., ge=0.0)
    error_rate: float = Field(..., ge=0.0, le=1.0)
    active_connections: int = Field(..., ge=0)
    uptime_seconds: float = Field(..., ge=0.0)
    disk_io_mbps: float = Field(0.0, ge=0.0)
    network_mbps: float = Field(0.0, ge=0.0)


class Alert(BaseModel):
    id: str
    severity: AlertSeverity
    service: str
    message: str
    timestamp: float
    acknowledged: bool = False


class AgentMessage(BaseModel):
    from_agent: AgentRole
    to_agent: Optional[AgentRole] = None
    content: str
    step: int
    message_type: str = "info"


class NoiseEvent(BaseModel):
    source: Literal["support_ticket", "twitter", "slack_alert", "email", "pagerduty", "jira"]
    content: str
    priority: str = "low"


class JiraTicket(BaseModel):
    id: str
    title: str
    status: str = "open"
    assignee: Optional[str] = None
    description: str = ""


class PRReview(BaseModel):
    pr_id: str
    status: str = "pending"
    comments: List[str] = Field(default_factory=list)
    test_results: Optional[Dict[str, bool]] = None
    style_score: float = 0.0
    safety_score: float = 0.0


class ChaosEvent(BaseModel):
    step: int
    event_type: str
    description: str
    impact: str


class MetricSnapshot(BaseModel):
    """Before/after metric snapshot for proof-of-fix scoring."""
    cpu_percent: float
    memory_percent: float
    latency_ms: float
    error_rate: float


class SkillBreakdown(BaseModel):
    """Per-skill scores for interpretability dashboard."""
    root_cause_accuracy: float = Field(0.0, ge=0.0, le=1.0)
    debugging_efficiency: float = Field(0.0, ge=0.0, le=1.0)
    patch_quality: float = Field(0.0, ge=0.0, le=1.0)
    collaboration: float = Field(0.0, ge=0.0, le=1.0)
    noise_filtering: float = Field(0.0, ge=0.0, le=1.0)
    speed: float = Field(0.0, ge=0.0, le=1.0)


class FailureReport(BaseModel):
    """Failure explanation report — shown in replay and leaderboard."""
    root_cause: str = ""
    agent_identified_root_cause: bool = False
    wrong_actions: List[str] = Field(default_factory=list)
    optimal_path: List[str] = Field(default_factory=list)
    final_verdict: str = "unknown"  # success | partial_success | failure
    metric_improvement: Optional[Dict[str, Any]] = None
    causal_link: Optional[str] = None
    confidence: float = 0.0


class Observation(BaseModel):
    step: int
    task_id: str
    metrics: SystemMetrics
    active_alerts: List[Alert] = Field(default_factory=list)
    recent_logs: List[str] = Field(default_factory=list)
    agent_messages: List[AgentMessage] = Field(default_factory=list)
    noise_events: List[NoiseEvent] = Field(default_factory=list)
    action_result: Optional[str] = None
    action_error: Optional[str] = None
    available_files: List[str] = Field(default_factory=list)
    escalated: bool = False
    escalation_hint: Optional[str] = None
    done: bool = False
    time_pressure: str = "normal"
    jira_tickets: List[JiraTicket] = Field(default_factory=list)
    pr_review: Optional[PRReview] = None
    chaos_events: List[ChaosEvent] = Field(default_factory=list)
    memory_hints: List[str] = Field(default_factory=list)
    difficulty_level: float = Field(1.0, description="Dynamic difficulty 0.5-2.0")
    ci_status: Optional[str] = None
    # Adversarial agent hint (may be wrong — agent must evaluate critically)
    adversarial_hint: Optional[str] = None
    seed: Optional[int] = None


class Reward(BaseModel):
    total: float = Field(..., ge=0.0, le=1.0)
    # Core components
    patch_correctness: float = Field(0.0, ge=0.0, le=1.0)
    hidden_tests_passed: float = Field(0.0, ge=0.0, le=1.0)
    metric_improvement: float = Field(0.0, ge=0.0, le=1.0, description="Before/after metric score")
    root_cause_identified: float = Field(0.0, ge=0.0, le=1.0)
    steps_efficiency: float = Field(0.0, ge=0.0, le=1.0)
    # Bonuses
    no_regression: float = Field(0.0, ge=0.0, le=1.0)
    explainability_score: float = Field(0.0, ge=0.0, le=1.0)
    safety_score: float = Field(0.0, ge=0.0, le=1.0)
    collaboration_score: float = Field(0.0, ge=0.0, le=1.0)
    noise_filtering_score: float = Field(0.0, ge=0.0, le=1.0, description="Ignored adversarial hints")
    # Penalties
    escalation_penalty: float = Field(0.0, ge=-1.0, le=0.0)
    # Metadata
    reason: str = ""
    skill_breakdown: Optional[SkillBreakdown] = None
    failure_report: Optional[FailureReport] = None
    post_mortem: Optional[Dict[str, Any]] = None
    pr_review: Optional[PRReview] = None


class FeedbackRequest(BaseModel):
    run_id: str
    rating: Literal["thumbs_up", "thumbs_down", "neutral"]
    comment: Optional[str] = None
    correct_fix: Optional[str] = None
    suggested_improvement: Optional[str] = None


class CustomScenarioRequest(BaseModel):
    name: str
    description: str
    difficulty: Literal["easy", "medium", "hard"]
    buggy_file_path: str
    buggy_code: str
    fixed_code: str
    initial_logs: List[str]
    root_cause_hint: str
    test_patterns: List[str] = Field(default_factory=list)


class EpisodeTrace(BaseModel):
    """Full episode trace for export — usable for RL training."""
    run_id: str
    task_id: str
    model: str
    seed: int
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    final_reward: float = 0.0
    skill_breakdown: Optional[SkillBreakdown] = None
    failure_report: Optional[FailureReport] = None
    duration_s: float = 0.0
