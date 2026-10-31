import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from gigsim.models import Job, ClientProfile, ProposalSubmission, ProposalResult, Message, ConnectsBalance, ClientDecision
from gigsim.store import store
from gigsim.client_evaluator import ClientEvaluator

app = FastAPI(
    title="GigSim Marketplace Simulator",
    description="Official GigSim REST API Stand-in for AI-4016 Freelancer Copilot Grading and Dev",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated rate limiter
REQUEST_COUNTS: Dict[str, List[float]] = {}
RATE_LIMIT_PER_MINUTE = 120
SIMULATE_ERRORS = {"500": False, "429": False}

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    timestamps = REQUEST_COUNTS.setdefault(client_ip, [])
    # Keep only last 60 seconds
    REQUEST_COUNTS[client_ip] = [ts for ts in timestamps if now - ts < 60.0]
    
    if SIMULATE_ERRORS["429"] or len(REQUEST_COUNTS[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="GigSim Rate Limit Exceeded: Max requests per minute reached.")
    if SIMULATE_ERRORS["500"]:
        raise HTTPException(status_code=500, detail="GigSim Simulated Internal Server Error (Chaos Test).")
    
    REQUEST_COUNTS[client_ip].append(now)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "gigsim",
        "jobs_loaded": len(store.jobs),
        "clients_loaded": len(store.clients)
    }

@app.get("/api/jobs", response_model=List[Job], dependencies=[Depends(check_rate_limit)])
def search_jobs(
    q: Optional[str] = Query(None, description="Search keyword in title/description"),
    persona: Optional[str] = Query(None, description="Target persona filter"),
    limit: int = Query(25, ge=1, le=100)
):
    return store.search_jobs(query=q, persona=persona, limit=limit)

@app.get("/api/jobs/{job_id}", response_model=Job, dependencies=[Depends(check_rate_limit)])
def get_job(job_id: str):
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found in GigSim.")
    return job

@app.get("/api/clients/{client_id}", response_model=ClientProfile, dependencies=[Depends(check_rate_limit)])
def get_client(client_id: str):
    client = store.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found in GigSim.")
    return client

@app.get("/api/connects/balance", response_model=ConnectsBalance, dependencies=[Depends(check_rate_limit)])
def get_connects_balance():
    return store.get_connects()

@app.post("/api/proposals/submit", response_model=ProposalResult, dependencies=[Depends(check_rate_limit)])
def submit_proposal(
    submission: ProposalSubmission,
    x_trace_id: Optional[str] = Header(None)
):
    try:
        result = store.submit_proposal(submission, trace_id=x_trace_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/messages", response_model=List[Message], dependencies=[Depends(check_rate_limit)])
def get_messages(client_id: str, job_id: str):
    return store.get_messages(client_id=client_id, job_id=job_id)

@app.post("/api/messages/send", response_model=Message, dependencies=[Depends(check_rate_limit)])
def send_message(
    payload: Dict[str, Any],
    x_trace_id: Optional[str] = Header(None)
):
    client_id = payload.get("client_id")
    job_id = payload.get("job_id")
    sender = payload.get("sender", "freelancer")
    text = payload.get("text", "")
    if not client_id or not job_id or not text:
        raise HTTPException(status_code=400, detail="client_id, job_id, and text are required.")
    return store.send_message(client_id=client_id, job_id=job_id, sender=sender, text=text, trace_id=x_trace_id)

@app.post("/api/simulate/evaluate", response_model=ClientDecision, dependencies=[Depends(check_rate_limit)])
def evaluate_proposal(submission: ProposalSubmission):
    job = store.get_job(submission.job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{submission.job_id}' not found.")
    return ClientEvaluator.evaluate(job, submission)

@app.get("/api/audit_logs")
def get_audit_logs():
    return store.audit_log

@app.post("/api/admin/chaos")
def set_chaos(simulate_500: bool = False, simulate_429: bool = False):
    SIMULATE_ERRORS["500"] = simulate_500
    SIMULATE_ERRORS["429"] = simulate_429
    return {"status": "chaos_updated", "flags": SIMULATE_ERRORS}
