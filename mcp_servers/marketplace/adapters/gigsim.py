import os
import httpx
from typing import Dict, List, Any, Optional
from gigsim.store import store
from gigsim.models import ProposalSubmission

class GigSimAdapter:
    def __init__(self, base_url: str = "http://localhost:8001", use_http: bool = False):
        self.base_url = base_url
        self.use_http = use_http

    async def search_jobs(self, query: Optional[str] = None, persona: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
        if self.use_http:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.get("/api/jobs", params={"q": query, "persona": persona, "limit": limit})
                res.raise_for_status()
                return res.json()
        jobs = store.search_jobs(query=query, persona=persona, limit=limit)
        return [j.model_dump() for j in jobs]

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        if self.use_http:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.get(f"/api/jobs/{job_id}")
                if res.status_code == 404:
                    return None
                res.raise_for_status()
                return res.json()
        job = store.get_job(job_id)
        return job.model_dump() if job else None

    async def get_client_history(self, client_id: str) -> Optional[Dict[str, Any]]:
        if self.use_http:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.get(f"/api/clients/{client_id}")
                if res.status_code == 404:
                    return None
                res.raise_for_status()
                return res.json()
        client = store.get_client(client_id)
        return client.model_dump() if client else None

    async def get_connects_balance(self) -> Dict[str, Any]:
        if self.use_http:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.get("/api/connects/balance")
                res.raise_for_status()
                return res.json()
        return store.get_connects().model_dump()

    async def submit_proposal(self, submission_data: Dict[str, Any], trace_id: Optional[str] = None) -> Dict[str, Any]:
        if self.use_http:
            headers = {"X-Trace-Id": trace_id} if trace_id else {}
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.post("/api/proposals/submit", json=submission_data, headers=headers)
                res.raise_for_status()
                return res.json()
        sub = ProposalSubmission(**submission_data)
        res = store.submit_proposal(sub, trace_id=trace_id)
        return res.model_dump()

    async def send_message(self, client_id: str, job_id: str, text: str, sender: str = "freelancer", trace_id: Optional[str] = None) -> Dict[str, Any]:
        if self.use_http:
            headers = {"X-Trace-Id": trace_id} if trace_id else {}
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.post("/api/messages/send", json={"client_id": client_id, "job_id": job_id, "text": text, "sender": sender}, headers=headers)
                res.raise_for_status()
                return res.json()
        msg = store.send_message(client_id=client_id, job_id=job_id, sender=sender, text=text, trace_id=trace_id)
        return msg.model_dump()

    async def list_messages(self, client_id: str, job_id: str) -> List[Dict[str, Any]]:
        if self.use_http:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                res = await client.get("/api/messages", params={"client_id": client_id, "job_id": job_id})
                res.raise_for_status()
                return res.json()
        msgs = store.get_messages(client_id=client_id, job_id=job_id)
        return [m.model_dump() for m in msgs]
