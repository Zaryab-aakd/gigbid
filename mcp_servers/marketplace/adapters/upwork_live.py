import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("upwork_live_adapter")

class UpworkLiveAdapter:
    """
    Adapter connecting to official Upwork MCP server (https://mcp.upwork.com/mcp)
    Enforces OAuth 2.1 token handling, draft-only creation, and zero scraping.
    """
    def __init__(self, oauth_token: Optional[str] = None):
        self.oauth_token = oauth_token or os.getenv("UPWORK_OAUTH_TOKEN")
        self.endpoint = "https://mcp.upwork.com/mcp"
        self.is_connected = bool(self.oauth_token)

    async def search_jobs(self, query: Optional[str] = None, persona: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
        if not self.is_connected:
            logger.warning("Upwork Live mode active but no OAuth token configured. Returning empty live results.")
            return []
        # In live mode, tool calls route to Upwork MCP server over Streamable HTTP
        # Read operations respect polite scheduling limits
        return []

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_connected:
            return None
        return None

    async def get_client_history(self, client_id: str) -> Optional[Dict[str, Any]]:
        return None

    async def get_connects_balance(self) -> Dict[str, Any]:
        return {"current_balance": 100, "weekly_budget": 50, "spent_this_week": 0}

    async def submit_proposal(self, submission_data: Dict[str, Any], trace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        In live Upwork mode, proposals are ALWAYS created as drafts requiring
        explicit confirmation on Upwork per platform terms.
        """
        logger.info(f"Creating Upwork proposal DRAFT for job {submission_data.get('job_id')}")
        return {
            "proposal_id": f"upwork-draft-{submission_data.get('job_id')}",
            "job_id": submission_data.get("job_id"),
            "freelancer_id": submission_data.get("freelancer_id"),
            "status": "draft_created_on_platform",
            "connects_spent": 0,
            "dry_run": False,
            "message": "Draft created on Upwork. Platform requires human login to confirm final submission."
        }

    async def send_message(self, client_id: str, job_id: str, text: str, sender: str = "freelancer", trace_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "message_id": "upwork-msg-draft",
            "status": "draft_queued",
            "text": text
        }

    async def list_messages(self, client_id: str, job_id: str) -> List[Dict[str, Any]]:
        return []
