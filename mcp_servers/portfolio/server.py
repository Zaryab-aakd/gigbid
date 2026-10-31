from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from mcp_servers.portfolio.tools import search_evidence, get_case_study, list_skills
from mcp_servers.portfolio.resources import get_case_resource, get_proposal_resource
from mcp_servers.portfolio.prompts import get_screening_prompt, get_proposal_prompt

mcp = FastMCP("PortfolioServer", dependencies=["pydantic"])

# --- TOOLS ---
@mcp.tool(name="search_evidence", description="Search verified portfolio evidence matching a requirement or skill.")
def search_evidence_tool(
    requirement: str,
    k: int = 5,
    persona_id: str = "ai_ml_engineer",
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Search portfolio for evidence matching requirements, with outcomes and skills."""
    return search_evidence(requirement, k=k, persona_id=persona_id, filters=filters)

@mcp.tool(name="get_case_study", description="Retrieve the full markdown text of a verified case study.")
def get_case_study_tool(case_id: str, persona_id: str = "ai_ml_engineer") -> str:
    """Retrieve verified case study documentation by ID."""
    res = get_case_study(case_id, persona_id=persona_id)
    return res if res else f"Case study '{case_id}' not found."

@mcp.tool(name="list_skills", description="List all verified skills and frameworks for a persona.")
def list_skills_tool(persona_id: str = "ai_ml_engineer") -> List[str]:
    """Retrieve full list of verified skills."""
    return list_skills(persona_id=persona_id)

# --- RESOURCES ---
@mcp.resource("portfolio://case/{case_id}")
def case_resource(case_id: str) -> str:
    """Load full case study resource."""
    return get_case_resource(case_id)

@mcp.resource("portfolio://proposal/{proposal_id}")
def proposal_resource(proposal_id: str) -> str:
    """Load historical proposal outcome and text."""
    return get_proposal_resource(proposal_id)

# --- PROMPTS ---
@mcp.prompt(name="answer_screening_question")
def screening_question_prompt(question: str, skills_needed: str) -> str:
    """Template for answering client screening questions with grounded evidence."""
    return get_screening_prompt(question, skills_needed)

@mcp.prompt(name="draft_grounded_proposal")
def proposal_draft_prompt(job_title: str, requirements: str) -> str:
    """Template for drafting evidence-grounded proposals."""
    return get_proposal_prompt(job_title, requirements)

if __name__ == "__main__":
    mcp.run()
