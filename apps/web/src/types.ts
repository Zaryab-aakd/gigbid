export interface JobInboxItem {
  job_id: string;
  title: string;
  description: string;
  required_skills: string[];
  budget_display: string;
  connects_cost: number;
  fit_score: number;
  risk_badge: "VERIFIED_SAFE" | "HIGH_RISK" | "INJECTION_BLOCKED";
  recommended_action: string;
  pipeline_status: string;
}

export interface MatrixItem {
  requirement: string;
  matched_evidence_id: string;
  evidence_title: string;
  outcome: string;
  status: "grounded" | "gap";
}

export interface JobDetailData {
  job: {
    job_id: string;
    title: string;
    description: string;
    required_skills: string[];
    budget: { min: number; max: number; currency: string };
    duration_days: number;
    screening_questions: string[];
  };
  client: {
    client_id: string;
    name: string;
    total_spend: number;
    hires: number;
    hire_rate: number;
    rating: number;
    payment_verified: boolean;
  };
  requirement_evidence_matrix: MatrixItem[];
  pipeline_card?: any;
}

export interface PendingProposalData {
  thread_id: string;
  is_paused_for_approval: boolean;
  job: {
    job_id: string;
    title: string;
  };
  cover_letter: string;
  screening_answers: string[];
  evidence_cited: Array<{
    evidence_id: string;
    title: string;
    outcome: string;
    skills: string[];
  }>;
  pricing: {
    recommended_bid: number;
    min_bid: number;
    max_bid: number;
    connects_cost: number;
    expected_roi_score: number;
    rationale: string;
  };
  critique: {
    passed: boolean;
    score: number;
    feedback: string;
    iteration_count: number;
  };
  compliance: {
    compliant: boolean;
    violations: string[];
    actions_taken: string[];
  };
  interrupt_details: any;
}

export interface MessageThreadItem {
  client_id: string;
  job_id: string;
  client_name: string;
  last_message: string;
  timestamp: string;
  suggested_reply: string;
}

export interface AnalyticsData {
  reply_rate_pct: number;
  hire_rate_pct: number;
  total_proposals_sent: number;
  connects_spent: number;
  connects_roi: string;
  avg_latency_seconds: number;
  cost_per_proposal_usd: number;
  rejection_breakdown: Array<{ reason: string; pct: number }>;
}

export interface LearnedMemoryItem {
  memory_id: string;
  type: "style" | "outcome";
  rule?: string;
  preference?: string;
  evidence_id?: string;
  evidence_ids?: string[];
  outcome?: string;
  created_at: string;
}

export interface UserProfileData {
  user: {
    user_id: string;
    name: string;
    active_persona: string;
    marketplace_mode: string;
    weekly_connects_budget: number;
    autonomy_level: string;
  };
  connects: {
    current_balance: number;
    weekly_budget: number;
    spent_this_week: number;
  };
}
