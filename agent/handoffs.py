from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class JobSpec(BaseModel):
    job_id: str
    title: str
    deliverables: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    screening_questions: List[str] = Field(default_factory=list)
    connects_cost: int = 6

class RiskReport(BaseModel):
    score: float = Field(ge=0, le=1, description="Risk probability score (0: safe, 1: dangerous)")
    is_scam: bool = False
    prompt_injection_detected: bool = False
    flags: List[str] = Field(default_factory=list)
    sanitized_description: str = ""
    explanation: str = ""

class FitReport(BaseModel):
    score: float = Field(ge=0, le=1, description="Portfolio fit score (0: none, 1: perfect match)")
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    reasons: str = ""

class PricingQuote(BaseModel):
    recommended_bid: float
    min_bid: float
    max_bid: float
    connects_cost: int
    expected_roi_score: float
    rationale: str

class ProposalDraft(BaseModel):
    job_id: str
    freelancer_id: str
    cover_letter: str
    screening_answers: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    status: str = "pending_review"

class ClaimVerificationReport(BaseModel):
    claims_total: int = 0
    supported_count: int = 0
    unsupported_count: int = 0
    claims_detail: List[Dict[str, Any]] = Field(default_factory=list)

class CritiqueReport(BaseModel):
    passed: bool
    score: float = Field(ge=0, le=1)
    feedback: str
    iteration_count: int = 0

class ComplianceVerdict(BaseModel):
    compliant: bool
    violations: List[str] = Field(default_factory=list)
    sanitized_letter: str = ""
    actions_taken: List[str] = Field(default_factory=list)
