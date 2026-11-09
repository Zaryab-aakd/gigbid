import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query, Header, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph
from agent.memory.store import memory_store
from mcp_servers.marketplace.server import (
    search_jobs_tool,
    get_job_tool,
    get_client_history_tool,
    get_connects_balance_tool,
    submit_proposal_tool,
    send_message_tool,
    list_messages_tool
)
from mcp_servers.workspace.server import (
    get_calendar_availability,
    create_interview_hold,
    list_workspace_activity
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

app = FastAPI(
    title="GigBid Copilot API",
    description="Backend API powering GigBid Multi-Agent Copilot with LangGraph interrupts and SSE Streaming",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Persistent in-memory graphs
SHARED_CHECKPOINTER = MemorySaver()
BID_GRAPH = build_bid_graph(checkpointer=SHARED_CHECKPOINTER)
CONV_GRAPH = build_conversation_graph(checkpointer=SHARED_CHECKPOINTER)

# Active pipeline jobs tracking
PIPELINE_STAGES = ["drafted", "submitted", "viewed", "replied", "interview", "hired", "lost"]
PIPELINE_BOARD: Dict[str, Dict[str, Any]] = {}

# Current user session
CURRENT_USER = {
    "user_id": "usr-01",
    "name": "Dr. Alex Rivera",
    "active_persona": "ai_ml_engineer",
    "marketplace_mode": "gigsim",
    "weekly_connects_budget": 80,
    "autonomy_level": "collaborative"  # collaborative, conservative, autonomous
}

# --- HEALTH & STATUS ---
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "gigbid-api",
        "active_persona": CURRENT_USER["active_persona"],
        "marketplace_mode": CURRENT_USER["marketplace_mode"]
    }

# --- USER PROFILE & ONBOARDING ---
@app.get("/api/user/profile")
def get_user_profile():
    balance = get_connects_balance_tool()
    return {
        "user": CURRENT_USER,
        "connects": balance
    }

@app.post("/api/user/switch_persona")
def switch_persona(persona_id: str = Query("ai_ml_engineer")):
    CURRENT_USER["active_persona"] = persona_id
    names = {
        "ai_ml_engineer": "Dr. Alex Rivera (AI/ML Engineer)",
        "full_stack_developer": "Jordan Lee (Full-Stack Engineer)",
        "data_analyst": "Maya Patel (Senior Data Analyst)"
    }
    CURRENT_USER["name"] = names.get(persona_id, "Freelancer")
    return {"status": "persona_switched", "current_user": CURRENT_USER}

# --- INBOX & JOBS ---
@app.get("/api/jobs/inbox")
def get_job_inbox(
    q: Optional[str] = None,
    filter_status: Optional[str] = None,
    limit: int = 30
):
    """
    Returns jobs scored and ranked for the active persona with risk badges.
    """
    persona = CURRENT_USER["active_persona"]
    raw_jobs = search_jobs_tool(query=q, persona=persona, limit=limit)
    inbox_items = []

    for j in raw_jobs:
        job_id = j.get("job_id")
        desc = j.get("description", "").lower()
        skills = j.get("required_skills", [])

        # Heuristic preview score for inbox display
        is_scam = any(kw in desc for kw in ["telegram", "whatsapp", "crypto", "free trial", "wire"])
        has_injection = any(kw in desc for kw in ["system override", "ignore previous"])
        fit_score = 0.88 if not is_scam else 0.20

        # Action recommendation
        if is_scam:
            rec_action = "SKIP (Scam)"
            risk_badge = "HIGH_RISK"
        elif has_injection:
            rec_action = "BID (Sanitized)"
            risk_badge = "INJECTION_BLOCKED"
        else:
            rec_action = "RECOMMENDED BID"
            risk_badge = "VERIFIED_SAFE"

        b_info = j.get("budget", {})
        price_display = f"${b_info.get('min', 500)} - ${b_info.get('max', 1500)}"

        inbox_items.append({
            "job_id": job_id,
            "title": j.get("title"),
            "description": j.get("description"),
            "required_skills": skills,
            "budget_display": price_display,
            "connects_cost": j.get("connects_cost", 6),
            "fit_score": fit_score,
            "risk_badge": risk_badge,
            "recommended_action": rec_action,
            "pipeline_status": PIPELINE_BOARD.get(job_id, {}).get("stage", "inbox")
        })

    return inbox_items

# --- JOB DETAIL & REQUIREMENT-TO-EVIDENCE MATRIX ---
@app.get("/api/jobs/{job_id}/detail")
def get_job_detail(job_id: str):
    job = get_job_tool(job_id)
    if "error" in job:
        raise HTTPException(status_code=404, detail=job["error"])

    client_id = job.get("client", {}).get("client_id", "client-unknown")
    client_info = get_client_history_tool(client_id)

    # Matrix linking each required skill to a verified portfolio evidence item
    from mcp_servers.portfolio.tools import search_evidence
    matrix = []
    persona = CURRENT_USER["active_persona"]
    for req in job.get("required_skills", []):
        hits = search_evidence(req, k=1, persona_id=persona)
        top_hit = hits[0] if hits else {}
        matrix.append({
            "requirement": req,
            "matched_evidence_id": top_hit.get("evidence_id") or top_hit.get("chunk_id", "N/A"),
            "evidence_title": top_hit.get("title", "No direct match"),
            "outcome": top_hit.get("outcome", "Pending review"),
            "status": "grounded" if top_hit else "gap"
        })

    return {
        "job": job,
        "client": client_info,
        "requirement_evidence_matrix": matrix,
        "pipeline_card": PIPELINE_BOARD.get(job_id)
    }

# --- LANGGRAPH STREAMING EXECUTION ---
@app.get("/api/stream/bid/{job_id}")
async def stream_bid_run(job_id: str):
    """
    Server-Sent Events (SSE) streaming live node-by-node LangGraph progress.
    """
    job = get_job_tool(job_id)
    if "error" in job:
        raise HTTPException(status_code=404, detail=job["error"])

    thread_id = f"thread-bid-{job_id}"
    config = {"configurable": {"thread_id": thread_id}}
    state_in = {
        "job": job,
        "persona_id": CURRENT_USER["active_persona"],
        "trace_id": str(uuid.uuid4())
    }

    async def event_generator():
        yield f"data: {json.dumps({'event': 'start', 'thread_id': thread_id, 'job_id': job_id})}\n\n"
        
        # Execute LangGraph steps
        for event in BID_GRAPH.stream(state_in, config, stream_mode="updates"):
            for node_name, node_update in event.items():
                node_summary = {
                    "node": node_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "completed"
                }
                if node_name == "decision":
                    node_summary["decision"] = node_update.get("decision")
                    node_summary["reason"] = node_update.get("decision_reason")
                elif node_name == "pricing":
                    quote = node_update.get("price_quote")
                    node_summary["recommended_bid"] = quote.recommended_bid if quote else 1000
                elif node_name == "writer":
                    draft = node_update.get("proposal_draft")
                    node_summary["preview_opening"] = draft.cover_letter[:120] if draft else ""
                elif node_name == "verifier":
                    vr = node_update.get("claim_verification")
                    node_summary["supported_claims"] = vr.supported_count if vr else 0
                    node_summary["unsupported_claims"] = vr.unsupported_count if vr else 0
                elif node_name == "critic":
                    cr = node_update.get("critique")
                    node_summary["passed"] = cr.passed if cr else True
                    node_summary["score"] = cr.score if cr else 1.0

                yield f"data: {json.dumps({'event': 'node_update', 'payload': node_summary})}\n\n"
                await asyncio.sleep(0.1)

        # Inspect if graph paused at interrupt
        curr_state = BID_GRAPH.get_state(config)
        if len(curr_state.next) > 0 and curr_state.next[0] == "human_approval":
            tasks = curr_state.tasks
            interrupt_val = tasks[0].interrupts[0].value if tasks and tasks[0].interrupts else {}
            yield f"data: {json.dumps({'event': 'interrupt_pending_approval', 'payload': interrupt_val})}\n\n"
        else:
            yield f"data: {json.dumps({'event': 'finished', 'final_decision': curr_state.values.get('decision')})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- PROPOSAL STUDIO & APPROVALS ---
@app.get("/api/proposals/{thread_id}/pending")
def get_pending_proposal(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = BID_GRAPH.get_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="No active graph thread found.")
    
    tasks = state.tasks
    interrupt_info = tasks[0].interrupts[0].value if tasks and tasks[0].interrupts else {}
    draft = state.values.get("proposal_draft")
    quote = state.values.get("price_quote")
    evidence = state.values.get("evidence", [])

    return {
        "thread_id": thread_id,
        "is_paused_for_approval": len(state.next) > 0 and state.next[0] == "human_approval",
        "job": state.values.get("job"),
        "cover_letter": draft.cover_letter if draft else "",
        "screening_answers": draft.screening_answers if draft else [],
        "evidence_cited": evidence,
        "pricing": quote.model_dump() if quote else {},
        "critique": state.values.get("critique", {}).model_dump() if state.values.get("critique") else {},
        "compliance": state.values.get("compliance_verdict", {}).model_dump() if state.values.get("compliance_verdict") else {},
        "interrupt_details": interrupt_info
    }

class ProposalApprovalBody(BaseModel):
    action: str = Field("approved", description="'approved' or 'rejected'")
    cover_letter: Optional[str] = None
    bid_amount: Optional[float] = None

@app.post("/api/proposals/{thread_id}/resume")
def resume_proposal_approval(thread_id: str, body: ProposalApprovalBody):
    config = {"configurable": {"thread_id": thread_id}}
    state = BID_GRAPH.get_state(config)
    if not state.values or len(state.next) == 0:
        raise HTTPException(status_code=400, detail="Graph is not currently paused at an interrupt.")

    # Record user edit to Style Memory if user modified the proposal text!
    original_draft = state.values.get("proposal_draft")
    if original_draft and body.cover_letter and body.cover_letter != original_draft.cover_letter:
        memory_store.record_user_edit(original_draft.cover_letter, body.cover_letter)

    approval_command = {
        "status": body.action,
        "cover_letter": body.cover_letter
    }

    # Resume graph execution
    events = list(BID_GRAPH.stream(Command(resume=approval_command), config, stream_mode="values"))
    final_state = BID_GRAPH.get_state(config)

    job_id = final_state.values.get("job", {}).get("job_id", "unknown")
    if body.action == "approved":
        PIPELINE_BOARD[job_id] = {
            "job_id": job_id,
            "title": final_state.values.get("job", {}).get("title"),
            "stage": "submitted",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "bid_amount": body.bid_amount or 1000.0
        }
    else:
        PIPELINE_BOARD[job_id] = {
            "job_id": job_id,
            "title": final_state.values.get("job", {}).get("title"),
            "stage": "lost",
            "reason": "User rejected proposal in studio"
        }

    return {
        "status": "resumed",
        "final_approval_status": final_state.values.get("approval_status"),
        "pipeline_card": PIPELINE_BOARD.get(job_id)
    }

# --- PIPELINE KANBAN BOARD ---
@app.get("/api/pipeline/board")
def get_pipeline_board():
    # Group items by stage
    board: Dict[str, List[Dict[str, Any]]] = {stage: [] for stage in PIPELINE_STAGES}
    for card in PIPELINE_BOARD.values():
        stage = card.get("stage", "drafted")
        if stage in board:
            board[stage].append(card)
    return board

# --- MESSAGES & LIAISON ---
@app.get("/api/messages/threads")
def get_messages_threads():
    # Return mock or stored threads
    return [
        {
            "client_id": "client-acme-corp",
            "job_id": "dev-job-0001",
            "client_name": "Acme Corp Tech Lead",
            "last_message": "Hi, we liked your proposal! Are you free for a 30-minute Zoom call this week?",
            "timestamp": "2026-11-14T12:30:00Z",
            "suggested_reply": "Hi! Thank you for getting back to me. I'd be happy to hop on a call to discuss the project details. Here are a few slots: Friday 10:00 AM UTC, Monday 2:00 PM UTC."
        }
    ]

# --- MEMORY VIEWER & CONTROLS ---
@app.get("/api/memory")
def get_learned_memory():
    return {
        "memories": memory_store.list_all_memories()
    }

@app.delete("/api/memory/{memory_id}")
def delete_learned_memory(memory_id: str):
    success = memory_store.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory item not found.")
    return {"status": "deleted", "memory_id": memory_id}

# --- ANALYTICS ---
@app.get("/api/analytics")
def get_analytics():
    return {
        "reply_rate_pct": 92.0,
        "hire_rate_pct": 34.0,
        "total_proposals_sent": 48,
        "connects_spent": 288,
        "connects_roi": "4.8x",
        "avg_latency_seconds": 1.4,
        "cost_per_proposal_usd": 0.00,
        "rejection_breakdown": [
            {"reason": "Budget ceiling exceeded", "pct": 45},
            {"reason": "Competitor local timezone", "pct": 30},
            {"reason": "Project canceled by client", "pct": 25}
        ]
    }

# --- STATIC FILES (WEB SPA) ---
dist_path = "apps/web/dist"
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")


