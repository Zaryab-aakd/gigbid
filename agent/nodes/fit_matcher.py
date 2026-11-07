from typing import Dict, Any, List
from agent.handoffs import FitReport
from agent.state import GigBidState
from rag.retriever import PortfolioRetriever

def fit_matcher_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    persona_id = state.get("persona_id", "ai_ml_engineer")
    desc = state.get("risk_report", {}).sanitized_description if state.get("risk_report") else job.get("description", "")
    req_skills = job.get("required_skills", [])

    # Call RAG retriever (V3 cross-encoder or variant set in config)
    retriever = PortfolioRetriever(persona_id=persona_id, variant_name="v3_reranker")
    evidence_items = retriever.retrieve(desc, k=4)

    # Collect matched skills across retrieved evidence
    portfolio_skills = set()
    for item in evidence_items:
        for s in item.get("skills", []):
            portfolio_skills.add(s.lower())

    matched = [s for s in req_skills if s.lower() in portfolio_skills or any(s.lower() in item.get("title", "").lower() for item in evidence_items)]
    missing = [s for s in req_skills if s not in matched]

    if req_skills:
        skill_ratio = len(matched) / len(req_skills)
    else:
        skill_ratio = 0.85

    evidence_ids = [e.get("evidence_id") or e.get("chunk_id") for e in evidence_items]
    score = min(1.0, round(0.40 + (skill_ratio * 0.60), 2)) if evidence_ids else 0.20

    reasons = f"Matched {len(matched)}/{len(req_skills)} skills with {len(evidence_ids)} portfolio items."
    
    report = FitReport(
        score=score,
        matched_skills=matched,
        missing_skills=missing,
        evidence_ids=evidence_ids,
        reasons=reasons
    )
    return {
        "fit_report": report,
        "evidence": evidence_items
    }
