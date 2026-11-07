from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from agent.handoffs import (
    JobSpec,
    RiskReport,
    FitReport,
    PricingQuote,
    ProposalDraft,
    ClaimVerificationReport,
    CritiqueReport,
    ComplianceVerdict
)

class GigBidState(TypedDict, total=False):
    job: Dict[str, Any]
    persona_id: str
    job_spec: JobSpec
    risk_report: RiskReport
    fit_report: FitReport
    decision: str  # "bid", "skip", "watch"
    decision_reason: str
    evidence: List[Dict[str, Any]]
    price_quote: PricingQuote
    proposal_draft: ProposalDraft
    claim_verification: ClaimVerificationReport
    critique: CritiqueReport
    compliance_verdict: ComplianceVerdict
    approval_status: str  # "pending_approval", "approved", "rejected", "submitted"
    user_edits: Optional[str]
    errors: List[str]
    trace_id: str

class ConversationState(TypedDict, total=False):
    client_id: str
    job_id: str
    incoming_message: str
    intent: str  # "question", "interview_request", "negotiation", "spam"
    proposed_slots: List[Dict[str, str]]
    draft_reply: str
    approval_status: str  # "pending_approval", "approved", "rejected"
    trace_id: str
