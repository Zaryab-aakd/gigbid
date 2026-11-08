import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from agent.state import GigBidState
from agent.handoffs import ClaimVerificationReport
from agent.nodes.analyst import analyst_node
from agent.nodes.risk_assessor import risk_assessor_node
from agent.nodes.fit_matcher import fit_matcher_node
from agent.nodes.pricing import pricing_node
from agent.nodes.writer import writer_node
from agent.nodes.critic import critic_node
from agent.nodes.compliance import compliance_node
from rag.verify import verify_claims, sanitize_draft
from mcp_servers.marketplace.server import submit_proposal_tool

def decision_node(state: GigBidState) -> Dict[str, Any]:
    risk = state.get("risk_report")
    fit = state.get("fit_report")

    risk_score = risk.score if risk else 0.1
    is_scam = risk.is_scam if risk else False
    fit_score = fit.score if fit else 0.5

    if is_scam or risk_score >= 0.65:
        decision = "skip"
        reason = f"High risk detected (score: {risk_score}, scam={is_scam}): {risk.explanation if risk else ''}"
    elif fit_score < 0.55:
        decision = "skip"
        reason = f"Insufficient portfolio fit (score: {fit_score}): {fit.reasons if fit else ''}"
    elif fit_score < 0.65:
        decision = "watch"
        reason = f"Moderate fit (score: {fit_score}); queued for manual review."
    else:
        decision = "bid"
        reason = f"Strong portfolio match (fit: {fit_score}, risk: {risk_score}). Proceeding to pricing and proposal drafting."

    return {
        "decision": decision,
        "decision_reason": reason
    }

def verifier_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    evidence = state.get("evidence", [])
    if not draft:
        return {"claim_verification": ClaimVerificationReport()}

    results = verify_claims(draft.cover_letter, evidence)
    supported = sum(1 for r in results if r["status"] == "supported")
    unsupported = sum(1 for r in results if r["status"] == "unsupported")

    # Sanitize draft if unsupported claims exist
    if unsupported > 0:
        cleaned_letter = sanitize_draft(draft.cover_letter, results)
        draft.cover_letter = cleaned_letter

    report = ClaimVerificationReport(
        claims_total=len(results),
        supported_count=supported,
        unsupported_count=unsupported,
        claims_detail=results
    )
    return {
        "claim_verification": report,
        "proposal_draft": draft
    }

def human_approval_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    quote = state.get("price_quote")
    job = state.get("job", {})

    # Interruption payload surfaced to web UI / reviewer
    interrupt_payload = {
        "action": "proposal_approval_required",
        "job_id": job.get("job_id"),
        "title": job.get("title"),
        "cover_letter": draft.cover_letter if draft else "",
        "screening_answers": draft.screening_answers if draft else [],
        "evidence_ids": draft.evidence_ids if draft else [],
        "bid_amount": quote.recommended_bid if quote else 500.0,
        "connects_cost": quote.connects_cost if quote else 6
    }

    # LangGraph Human-in-the-Loop Interrupt
    user_decision = interrupt(interrupt_payload)

    # When graph resumes after user review:
    status = user_decision.get("status", "approved")
    edited_text = user_decision.get("cover_letter")
    if edited_text and draft:
        draft.cover_letter = edited_text

    return {
        "approval_status": status,
        "user_edits": edited_text
    }

def submit_proposal_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    quote = state.get("price_quote")
    job = state.get("job", {})
    trace_id = state.get("trace_id", str(uuid.uuid4()))

    if state.get("approval_status") == "approved" and draft:
        result = submit_proposal_tool(
            job_id=job.get("job_id"),
            freelancer_id=draft.freelancer_id,
            cover_letter=draft.cover_letter,
            bid_amount=quote.recommended_bid if quote else 1000.0,
            screening_answers=draft.screening_answers,
            evidence_ids=draft.evidence_ids,
            dry_run=False,
            idempotency_key=f"bid-{job.get('job_id')}-{draft.iteration_count}"
        )
        return {"approval_status": "submitted", "submission_result": result}
    
    return {"approval_status": state.get("approval_status", "rejected")}

# Routing functions
def route_decision(state: GigBidState) -> Literal["pricing", "end"]:
    if state.get("decision") == "bid":
        return "pricing"
    return "end"

def route_critic(state: GigBidState) -> Literal["writer", "compliance"]:
    critique = state.get("critique")
    if critique and not critique.passed and critique.iteration_count < 2:
        return "writer"
    return "compliance"

def route_approval(state: GigBidState) -> Literal["submit", "end"]:
    if state.get("approval_status") == "approved":
        return "submit"
    return "end"

def build_bid_graph(checkpointer=None):
    """
    Constructs the hand-written LangGraph StateGraph for the Bid Graph.
    Includes parallel Job Analyst, Risk Assessor, and Fit Matcher branches,
    decision routing, bounded Critic loop, Compliance Guard, and LangGraph interrupt() HITL.
    """
    workflow = StateGraph(GigBidState)

    # Add nodes
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk_assessor", risk_assessor_node)
    workflow.add_node("fit_matcher", fit_matcher_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("pricing", pricing_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("submit", submit_proposal_node)

    # Parallel fanout from START to analyst, risk_assessor, fit_matcher
    workflow.add_edge(START, "analyst")
    workflow.add_edge(START, "risk_assessor")
    workflow.add_edge(START, "fit_matcher")

    # Fanin to decision
    workflow.add_edge("analyst", "decision")
    workflow.add_edge("risk_assessor", "decision")
    workflow.add_edge("fit_matcher", "decision")

    # Routing from decision
    workflow.add_conditional_edges(
        "decision",
        route_decision,
        {"pricing": "pricing", "end": END}
    )

    # Linear pipeline
    workflow.add_edge("pricing", "writer")
    workflow.add_edge("writer", "verifier")
    workflow.add_edge("verifier", "critic")

    # Critic bounded loop
    workflow.add_conditional_edges(
        "critic",
        route_critic,
        {"writer": "writer", "compliance": "compliance"}
    )

    # Compliance to Human Approval Interrupt
    workflow.add_edge("compliance", "human_approval")

    # Approval to Submit
    workflow.add_conditional_edges(
        "human_approval",
        route_approval,
        {"submit": "submit", "end": END}
    )

    workflow.add_edge("submit", END)

    cp = checkpointer or MemorySaver()
    return workflow.compile(checkpointer=cp)
