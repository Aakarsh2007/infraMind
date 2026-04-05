export interface SystemMetrics {
  cpu_percent: number; memory_percent: number; latency_ms: number
  error_rate: number; active_connections: number; uptime_seconds: number
  disk_io_mbps: number; network_mbps: number
}
export interface Alert { id: string; severity: string; service: string; message: string; timestamp: number; acknowledged: boolean }
export interface AgentMessage { from_agent: string; to_agent: string|null; content: string; step: number; message_type: string }
export interface NoiseEvent { source: string; content: string; priority: string }
export interface JiraTicket { id: string; title: string; status: string; assignee: string|null; description: string }
export interface PRReview { pr_id: string; status: string; comments: string[]; test_results: Record<string,boolean>|null; style_score: number; safety_score: number }
export interface ChaosEvent { step: number; event_type: string; description: string; impact: string }

export interface SkillBreakdown {
  root_cause_accuracy: number; debugging_efficiency: number; patch_quality: number
  collaboration: number; noise_filtering: number; speed: number
}

export interface FailureReport {
  root_cause: string; agent_identified_root_cause: boolean
  wrong_actions: string[]; optimal_path: string[]
  final_verdict: string; metric_improvement: Record<string, unknown> | null
  causal_link: string | null; confidence: number
}

export interface Observation {
  step: number; task_id: string; metrics: SystemMetrics
  active_alerts: Alert[]; recent_logs: string[]; agent_messages: AgentMessage[]
  noise_events: NoiseEvent[]; action_result: string|null; action_error: string|null
  available_files: string[]; escalated: boolean; escalation_hint: string|null
  done: boolean; time_pressure: string; jira_tickets: JiraTicket[]
  pr_review: PRReview|null; chaos_events: ChaosEvent[]; memory_hints: string[]
  difficulty_level: number; ci_status: string|null
  adversarial_hint: string|null  // Wrong advice — agent must ignore
  seed: number|null
}

export interface Reward {
  total: number; patch_correctness: number; hidden_tests_passed: number
  metric_improvement: number; steps_efficiency: number; root_cause_identified: number
  no_regression: number; escalation_penalty: number; explainability_score: number
  safety_score: number; collaboration_score: number; noise_filtering_score: number
  reason: string
  skill_breakdown: SkillBreakdown | null
  failure_report: FailureReport | null
  post_mortem: Record<string,unknown>|null
  pr_review: PRReview|null
}

export interface StepResult { observation: Observation; reward: Reward; done: boolean; info: Record<string,unknown> }
export interface Task { id: string; name: string; difficulty: string; max_steps: number; description: string; tags?: string[] }
