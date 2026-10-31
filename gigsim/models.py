from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class ClientProfile(BaseModel):
    client_id: str
    name: str = "Confidential Client"
    total_spend: float = 0.0
    hires: int = 0
    hire_rate: float = 0.0
    rating: float = 5.0
    payment_verified: bool = True
    hidden_preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "budget_ceiling": 5000.0,
        "must_have_skills": [],
        "penalize_generic_opening": True,
        "prefers_evidence_citations": True
    })

class Job(BaseModel):
    job_id: str
    title: str
    description: str
    required_skills: List[str] = Field(default_factory=list)
    budget: Dict[str, Any] = Field(default_factory=lambda: {"min": 500, "max": 1500, "currency": "USD"})
    duration_days: int = 14
    connects_cost: int = 6
    screening_questions: List[str] = Field(default_factory=list)
    warning_signals: List[str] = Field(default_factory=list)
    target_persona: Optional[str] = None
    client: Optional[ClientProfile] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProposalSubmission(BaseModel):
    job_id: str
    freelancer_id: str
    cover_letter: str
    bid_amount: float
    screening_answers: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    dry_run: bool = False
    idempotency_key: str

class ProposalResult(BaseModel):
    proposal_id: str
    job_id: str
    freelancer_id: str
    status: str  # "draft", "submitted", "duplicate", "preview"
    connects_spent: int
    dry_run: bool
    submitted_at: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)

class Message(BaseModel):
    message_id: str
    thread_id: str
    sender: str  # "freelancer" or "client"
    text: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MessageThread(BaseModel):
    thread_id: str
    client_id: str
    job_id: str
    messages: List[Message] = Field(default_factory=list)

class ConnectsBalance(BaseModel):
    current_balance: int = 150
    weekly_budget: int = 80
    spent_this_week: int = 0

class ClientDecision(BaseModel):
    proposal_id: str
    job_id: str
    replied: bool
    interview_offered: bool
    hired: bool
    quality_score: float  # 0.0 to 1.0
    client_feedback: str
