import re
from typing import Dict, Any
from agent.handoffs import JobSpec
from agent.state import GigBidState

def analyst_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    title = job.get("title", "")
    desc = job.get("description", "")
    
    # Extract deliverables
    deliverables = []
    for line in desc.split("\n"):
        line_clean = line.strip("*-• ")
        if len(line_clean) > 15 and any(kw in line_clean.lower() for kw in ["build", "create", "implement", "deploy", "design", "deliver"]):
            deliverables.append(line_clean)
    if not deliverables:
        deliverables = [f"Deliver implementation for: {title}"]

    # Extract required skills
    skills = job.get("required_skills", [])
    if not skills:
        common_tech = ["Python", "FastAPI", "React", "Next.js", "TypeScript", "LangGraph", "LangChain", "SQL", "Docker", "PyTorch"]
        skills = [t for t in common_tech if t.lower() in desc.lower()]

    budget_info = job.get("budget", {})
    b_min = float(budget_info.get("min", 500))
    b_max = float(budget_info.get("max", 1500))

    spec = JobSpec(
        job_id=job.get("job_id", "unknown"),
        title=title,
        deliverables=deliverables[:5],
        required_skills=skills,
        budget_min=b_min,
        budget_max=b_max,
        screening_questions=job.get("screening_questions", []),
        connects_cost=job.get("connects_cost", 6)
    )
    return {"job_spec": spec}
