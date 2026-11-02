import os
import yaml
from typing import Protocol, Any, Dict, List, Optional
from mcp_servers.marketplace.adapters.gigsim import GigSimAdapter
from mcp_servers.marketplace.adapters.upwork_live import UpworkLiveAdapter

class MarketplacePort(Protocol):
    async def search_jobs(self, query: Optional[str] = None, persona: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]: ...
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]: ...
    async def get_client_history(self, client_id: str) -> Optional[Dict[str, Any]]: ...
    async def get_connects_balance(self) -> Dict[str, Any]: ...
    async def submit_proposal(self, submission_data: Dict[str, Any], trace_id: Optional[str] = None) -> Dict[str, Any]: ...
    async def send_message(self, client_id: str, job_id: str, text: str, sender: str = "freelancer", trace_id: Optional[str] = None) -> Dict[str, Any]: ...
    async def list_messages(self, client_id: str, job_id: str) -> List[Dict[str, Any]]: ...

def get_marketplace_adapter(mode: Optional[str] = None) -> MarketplacePort:
    if mode is None:
        # Load from config.yaml
        config_path = "agent/config.yaml"
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    cfg = yaml.safe_load(f)
                    mode = cfg.get("marketplace", {}).get("mode", "gigsim")
            except Exception:
                mode = "gigsim"
        else:
            mode = "gigsim"

    if mode == "upwork_live":
        return UpworkLiveAdapter()
    return GigSimAdapter()
