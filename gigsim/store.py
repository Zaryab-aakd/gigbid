import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from gigsim.models import Job, ClientProfile, ProposalSubmission, ProposalResult, MessageThread, Message, ConnectsBalance

class GigSimStore:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.clients: Dict[str, ClientProfile] = {}
        self.proposals: Dict[str, Dict[str, Any]] = {}
        self.idempotency_map: Dict[str, ProposalResult] = {}
        self.connects: ConnectsBalance = ConnectsBalance(current_balance=150, weekly_budget=80, spent_this_week=0)
        self.threads: Dict[str, MessageThread] = {}
        self.audit_log: List[Dict[str, Any]] = []

        self._load_seed_data()

    def _load_seed_data(self):
        # 1. Load dev set if present, else historical
        dev_path = "evals/datasets/dev_set_600_jobs.json"
        hist_path = "data/jobs/historical_1500_jobs.json"
        
        path_to_load = dev_path if os.path.exists(dev_path) else hist_path
        if os.path.exists(path_to_load):
            try:
                with open(path_to_load) as f:
                    data = json.load(f)
                    for item in data:
                        job_id = item["job_id"]
                        client_data = item.get("client", {})
                        client_id = client_data.get("client_id", f"client-{job_id}")
                        client = ClientProfile(
                            client_id=client_id,
                            total_spend=client_data.get("total_spend", 5000),
                            hires=client_data.get("hires", 5),
                            hire_rate=client_data.get("hire_rate", 0.75),
                            rating=client_data.get("rating", 4.9),
                            payment_verified=client_data.get("payment_verified", True)
                        )
                        self.clients[client_id] = client

                        job = Job(
                            job_id=job_id,
                            title=item["title"],
                            description=item["description"],
                            required_skills=item.get("required_skills", []),
                            budget=item.get("budget", {"min": 500, "max": 1500, "currency": "USD"}),
                            duration_days=item.get("duration_days", 14),
                            connects_cost=item.get("connects_cost", 6),
                            screening_questions=item.get("screening_questions", []),
                            warning_signals=item.get("warning_signals", []),
                            target_persona=item.get("persona_id") or item.get("target_persona"),
                            client=client
                        )
                        self.jobs[job_id] = job
            except Exception as e:
                print(f"Warning: Failed to load seed data into GigSimStore: {e}")

    def log_audit(self, user: str, tool: str, arguments: Dict[str, Any], result: Dict[str, Any], trace_id: Optional[str] = None):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user,
            "tool": tool,
            "arguments": arguments,
            "result": result,
            "trace_id": trace_id or str(uuid.uuid4())
        }
        self.audit_log.append(entry)

    def search_jobs(self, query: Optional[str] = None, persona: Optional[str] = None, limit: int = 50) -> List[Job]:
        results = list(self.jobs.values())
        if persona:
            results = [j for j in results if j.target_persona == persona or not j.target_persona]
        if query:
            q = query.lower()
            results = [j for j in results if q in j.title.lower() or q in j.description.lower() or any(q in s.lower() for s in j.required_skills)]
        return results[:limit]

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def get_client(self, client_id: str) -> Optional[ClientProfile]:
        return self.clients.get(client_id)

    def get_connects(self) -> ConnectsBalance:
        return self.connects

    def submit_proposal(self, sub: ProposalSubmission, trace_id: Optional[str] = None) -> ProposalResult:
        # Check idempotency first!
        if sub.idempotency_key in self.idempotency_map:
            cached = self.idempotency_map[sub.idempotency_key]
            self.log_audit(sub.freelancer_id, "submit_proposal [IDEMPOTENT CACHE HIT]", sub.model_dump(), cached.model_dump(), trace_id)
            return cached

        job = self.get_job(sub.job_id)
        connects_needed = job.connects_cost if job else 6

        if sub.dry_run:
            preview = ProposalResult(
                proposal_id=f"preview-{uuid.uuid4().hex[:8]}",
                job_id=sub.job_id,
                freelancer_id=sub.freelancer_id,
                status="preview",
                connects_spent=connects_needed,
                dry_run=True,
                submitted_at=datetime.now(timezone.utc).isoformat(),
                message=f"[DRY RUN] Proposal validated. Submitting will consume {connects_needed} Connects. Current balance: {self.connects.current_balance}.",
                details={"bid_amount": sub.bid_amount, "evidence_count": len(sub.evidence_ids)}
            )
            self.log_audit(sub.freelancer_id, "submit_proposal [DRY RUN]", sub.model_dump(), preview.model_dump(), trace_id)
            return preview

        # Deduct connects
        if self.connects.current_balance < connects_needed:
            raise ValueError(f"Insufficient Connects: Needed {connects_needed}, but balance is {self.connects.current_balance}")

        self.connects.current_balance -= connects_needed
        self.connects.spent_this_week += connects_needed

        prop_id = f"prop-{uuid.uuid4().hex[:8]}"
        res = ProposalResult(
            proposal_id=prop_id,
            job_id=sub.job_id,
            freelancer_id=sub.freelancer_id,
            status="submitted",
            connects_spent=connects_needed,
            dry_run=False,
            submitted_at=datetime.now(timezone.utc).isoformat(),
            message=f"Proposal submitted successfully! Spent {connects_needed} connects. Remaining: {self.connects.current_balance}.",
            details={"bid_amount": sub.bid_amount, "cover_letter": sub.cover_letter}
        )

        self.proposals[prop_id] = {
            "submission": sub.model_dump(),
            "result": res.model_dump()
        }
        self.idempotency_map[sub.idempotency_key] = res
        self.log_audit(sub.freelancer_id, "submit_proposal", sub.model_dump(), res.model_dump(), trace_id)
        return res

    def send_message(self, client_id: str, job_id: str, sender: str, text: str, trace_id: Optional[str] = None) -> Message:
        thread_key = f"{client_id}:{job_id}"
        if thread_key not in self.threads:
            self.threads[thread_key] = MessageThread(
                thread_id=f"thread-{uuid.uuid4().hex[:8]}",
                client_id=client_id,
                job_id=job_id,
                messages=[]
            )
        thread = self.threads[thread_key]
        msg = Message(
            message_id=f"msg-{uuid.uuid4().hex[:8]}",
            thread_id=thread.thread_id,
            sender=sender,
            text=text,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        thread.messages.append(msg)
        self.log_audit(sender, "send_message", {"client_id": client_id, "job_id": job_id, "text": text}, msg.model_dump(), trace_id)
        return msg

    def get_messages(self, client_id: str, job_id: str) -> List[Message]:
        thread_key = f"{client_id}:{job_id}"
        if thread_key in self.threads:
            return self.threads[thread_key].messages
        return []

# Global singleton store for simulator
store = GigSimStore()
