import json
import os
from typing import Optional
from mcp_servers.portfolio.tools import get_case_study, get_data_dir

def get_case_resource(case_id: str) -> str:
    content = get_case_study(case_id)
    if content:
        return content
    return f"Case study '{case_id}' not found in verified portfolio."

def get_proposal_resource(proposal_id: str) -> str:
    data_dir = get_data_dir()
    for persona_id in ["ai_ml_engineer", "full_stack_developer", "data_analyst"]:
        prop_path = os.path.join(data_dir, "personas", persona_id, "past_proposals.json")
        if os.path.exists(prop_path):
            with open(prop_path) as f:
                proposals = json.load(f)
                for p in proposals:
                    if p.get("proposal_id") == proposal_id:
                        return json.dumps(p, indent=2)
    return f"Proposal '{proposal_id}' not found in past proposal records."

