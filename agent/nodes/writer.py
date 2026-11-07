from typing import Dict, Any, List
from agent.handoffs import ProposalDraft
from agent.state import GigBidState

def writer_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    job_spec = state.get("job_spec")
    evidence = state.get("evidence", [])
    critique = state.get("critique")
    prev_draft = state.get("proposal_draft")

    iteration = (prev_draft.iteration_count + 1) if prev_draft else 1
    persona_id = state.get("persona_id", "ai_ml_engineer")
    title = job_spec.title if job_spec else job.get("title", "")
    skills = job_spec.required_skills if job_spec else job.get("required_skills", [])

    top_evidence = evidence[0] if evidence else {}
    evidence_id = top_evidence.get("evidence_id") or top_evidence.get("chunk_id", "portfolio-01")
    evidence_title = top_evidence.get("title", "similar production system")
    evidence_outcome = top_evidence.get("outcome", "verified production performance")

    # Tailored, grounded opening addressing technical challenge (no generic fluff!)
    opening = f"Hi there. I reviewed your requirements for {title}. Dealing with {', '.join(skills[:3])} in production requires careful attention to scalability and error handling."
    
    body = (
        f"In my verified project '{evidence_title}' [{evidence_id}], I implemented this architecture and achieved {evidence_outcome}. "
        f"For your project, I propose decomposing the deliverables into clear milestones, starting with an interface contract and baseline tests before scaling."
    )

    closing = "When is a convenient time this week for a brief technical call to review the specification?"

    cover_letter = f"{opening}\n\n{body}\n\n{closing}"

    # Screening answers
    screening_answers = []
    questions = job_spec.screening_questions if job_spec else job.get("screening_questions", [])
    for q in questions:
        screening_answers.append(
            f"Based on my delivery of '{evidence_title}', I approach this by designing modular pipelines with automated validation and unit test coverage."
        )

    draft = ProposalDraft(
        job_id=job.get("job_id", "unknown"),
        freelancer_id=persona_id,
        cover_letter=cover_letter,
        screening_answers=screening_answers,
        evidence_ids=[evidence_id] if evidence_id else [],
        iteration_count=iteration,
        status="drafted"
    )
    return {"proposal_draft": draft}
