import os
import uuid
import asyncio
import concurrent.futures
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from agent.marketplace_port import get_marketplace_adapter

mcp = FastMCP("MarketplaceServer", dependencies=["pydantic", "httpx"])

adapter = get_marketplace_adapter()

def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)

# --- INPUT SCHEMAS WITH CONSTRAINTS ---

class SearchJobsInput(BaseModel):
    query: Optional[str] = Field(None, description="Keywords to match in job title or description")
    persona: Optional[str] = Field(None, description="Filter for specific persona: ai_ml_engineer, full_stack_developer, or data_analyst")
    limit: int = Field(25, ge=1, le=100, description="Maximum number of jobs to return")

class GetJobInput(BaseModel):
    job_id: str = Field(..., min_length=3, description="Unique job identifier")

class GetClientHistoryInput(BaseModel):
    client_id: str = Field(..., min_length=3, description="Client identifier")

class SubmitProposalInput(BaseModel):
    job_id: str = Field(..., min_length=3, description="Target job ID")
    freelancer_id: str = Field(..., min_length=2, description="Freelancer submitting proposal")
    cover_letter: str = Field(..., min_length=20, max_length=5000, description="Proposal cover letter body")
    bid_amount: float = Field(..., gt=0, description="Proposed fixed bid amount in USD")
    screening_answers: List[str] = Field(default_factory=list, description="Answers to client screening questions")
    evidence_ids: List[str] = Field(default_factory=list, description="Citations of verified portfolio case studies")
    dry_run: bool = Field(False, description="If True, returns preview of costs without spending Connects or submitting")
    idempotency_key: str = Field(..., min_length=8, description="Unique UUID to prevent double submissions")

class SendMessageInput(BaseModel):
    client_id: str = Field(..., min_length=3, description="Client ID")
    job_id: str = Field(..., min_length=3, description="Associated job ID")
    text: str = Field(..., min_length=1, max_length=2000, description="Message text content")
    sender: str = Field("freelancer", description="Message sender")

class ListMessagesInput(BaseModel):
    client_id: str = Field(..., min_length=3)
    job_id: str = Field(..., min_length=3)

# --- MCP TOOLS WITH ANNOTATIONS ---

@mcp.tool(
    name="search_jobs",
    description="Search active freelance job postings on the marketplace."
)
def search_jobs_tool(query: Optional[str] = None, persona: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
    """Read-only search of available jobs."""
    return _run_async(adapter.search_jobs(query=query, persona=persona, limit=limit))

@mcp.tool(
    name="get_job",
    description="Fetch complete job post specifications, screening questions, and budget details."
)
def get_job_tool(job_id: str) -> Dict[str, Any]:
    """Read-only fetch of a single job."""
    res = _run_async(adapter.get_job(job_id))
    if not res:
        return {"error": f"Job '{job_id}' not found."}
    return res

@mcp.tool(
    name="get_client_history",
    description="Retrieve client spending history, hire rate, ratings, and past feedback."
)
def get_client_history_tool(client_id: str) -> Dict[str, Any]:
    """Read-only fetch of client background metrics."""
    res = _run_async(adapter.get_client_history(client_id))
    if not res:
        return {"error": f"Client '{client_id}' not found."}
    return res

@mcp.tool(
    name="get_connects_balance",
    description="Check remaining Connects balance and weekly budget limits."
)
def get_connects_balance_tool() -> Dict[str, Any]:
    """Read-only check of current Connects balance."""
    return _run_async(adapter.get_connects_balance())

@mcp.tool(
    name="submit_proposal",
    description="Submit a proposal for a job or run a dry_run preview. Requires explicit human approval and idempotency key."
)
def submit_proposal_tool(
    job_id: str,
    freelancer_id: str,
    cover_letter: str,
    bid_amount: float,
    idempotency_key: str,
    screening_answers: Optional[List[str]] = None,
    evidence_ids: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Submits proposal to the marketplace.
    Connects are deducted unless dry_run=True.
    Idempotent: repeating with same idempotency_key will not double-spend connects.
    """
    payload = {
        "job_id": job_id,
        "freelancer_id": freelancer_id,
        "cover_letter": cover_letter,
        "bid_amount": bid_amount,
        "screening_answers": screening_answers or [],
        "evidence_ids": evidence_ids or [],
        "dry_run": dry_run,
        "idempotency_key": idempotency_key
    }
    return _run_async(adapter.submit_proposal(payload))

@mcp.tool(
    name="send_message",
    description="Send a message to a client in an active conversation thread. Requires human approval."
)
def send_message_tool(client_id: str, job_id: str, text: str, sender: str = "freelancer") -> Dict[str, Any]:
    """Send client communication message."""
    return _run_async(adapter.send_message(client_id=client_id, job_id=job_id, text=text, sender=sender))

@mcp.tool(
    name="list_messages",
    description="Retrieve all messages exchanged in a client conversation thread."
)
def list_messages_tool(client_id: str, job_id: str) -> List[Dict[str, Any]]:
    """Read-only list of client messages."""
    return _run_async(adapter.list_messages(client_id=client_id, job_id=job_id))

if __name__ == "__main__":
    mcp.run()
