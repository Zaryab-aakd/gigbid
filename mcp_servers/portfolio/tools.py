import json
import os
import glob
from typing import List, Dict, Any, Optional

def load_persona_portfolio(persona_id: str = "ai_ml_engineer") -> List[Dict[str, Any]]:
    path = f"data/personas/{persona_id}/portfolio_items.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def search_evidence(requirement: str, k: int = 5, persona_id: str = "ai_ml_engineer", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Search verified portfolio evidence matching a specific requirement or skill.
    Returns evidence items with type, source, outcome, skills, and relevance.
    """
    items = load_persona_portfolio(persona_id)
    req_lower = requirement.lower()
    req_terms = set(req_lower.replace(",", " ").replace("/", " ").split())

    scored = []
    for item in items:
        # Check filters
        if filters:
            if "type" in filters and item.get("type") != filters["type"]:
                continue
            if "skill" in filters and filters["skill"].lower() not in [s.lower() for s in item.get("skills", [])]:
                continue

        text = f"{item.get('title', '')} {item.get('summary', '')} {' '.join(item.get('skills', []))} {item.get('outcome', '')}".lower()
        score = sum(1 for term in req_terms if term in text)
        if any(s.lower() in req_lower for s in item.get("skills", [])):
            score += 3
        
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [s[1] for s in scored[:k]]
    return results

def get_case_study(case_id: str, persona_id: str = "ai_ml_engineer") -> Optional[str]:
    """
    Load the full markdown text of a specific verified case study.
    """
    # Search in persona directories
    patterns = [
        f"data/personas/{persona_id}/case_studies/*{case_id}*.md",
        f"data/personas/*/case_studies/*{case_id}*.md"
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            with open(matches[0]) as f:
                return f.read()

    # Fallback search by title or id in portfolio_items.json
    for p in ["ai_ml_engineer", "full_stack_developer", "data_analyst"]:
        items = load_persona_portfolio(p)
        for it in items:
            if it.get("evidence_id") == case_id:
                return f"# {it.get('title')}\n\n**Outcome:** {it.get('outcome')}\n\n**Summary:** {it.get('summary')}\n\n**Skills:** {', '.join(it.get('skills', []))}"
    return None

def list_skills(persona_id: str = "ai_ml_engineer") -> List[str]:
    """
    List all verified competencies, frameworks, and skills for the freelancer persona.
    """
    items = load_persona_portfolio(persona_id)
    skills = set()
    for item in items:
        for s in item.get("skills", []):
            skills.add(s)
    return sorted(list(skills))
