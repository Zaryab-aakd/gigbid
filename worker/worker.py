import os
import time
import uuid
import logging
from typing import Dict, Any, List
from agent.graphs.bid_graph import build_bid_graph
from mcp_servers.marketplace.server import search_jobs_tool
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger("gigbid_worker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PROCESSED_JOB_IDS = set()

class GigBidWorker:
    def __init__(self, checkpointer=None):
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = build_bid_graph(checkpointer=self.checkpointer)

    def process_job_idempotent(self, job: Dict[str, Any], persona_id: str = "ai_ml_engineer") -> Dict[str, Any]:
        job_id = job.get("job_id")
        if job_id in PROCESSED_JOB_IDS:
            logger.info(f"[WORKER IDEMPOTENT SKIP] Job {job_id} already analyzed; skipping.")
            return {"status": "skipped_duplicate", "job_id": job_id}

        PROCESSED_JOB_IDS.add(job_id)
        thread_id = f"worker-thread-{job_id}"
        config = {"configurable": {"thread_id": thread_id}}
        state_in = {
            "job": job,
            "persona_id": persona_id,
            "trace_id": str(uuid.uuid4())
        }

        logger.info(f"[WORKER] Starting background copilot analysis for job {job_id}...")
        events = list(self.graph.stream(state_in, config))
        
        # Check if paused at interrupt or finished
        state = self.graph.get_state(config)
        is_paused = len(state.next) > 0 and state.next[0] == "human_approval"
        logger.info(f"[WORKER] Completed analysis for job {job_id}. Paused for approval: {is_paused}")
        
        return {
            "job_id": job_id,
            "thread_id": thread_id,
            "paused_for_approval": is_paused,
            "decision": state.values.get("decision")
        }

    def run_scheduled_scout(self, persona_id: str = "ai_ml_engineer", limit: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"[SCOUT] Polling marketplace for new opportunities for persona '{persona_id}'...")
        jobs = search_jobs_tool(persona=persona_id, limit=limit)
        results = []
        for j in jobs:
            res = self.process_job_idempotent(j, persona_id=persona_id)
            results.append(res)
        return results

if __name__ == "__main__":
    worker = GigBidWorker()
    logger.info("GigBid Worker & Scheduler started.")
    worker.run_scheduled_scout(persona_id="ai_ml_engineer", limit=3)
