import re
from typing import Dict, Any
from agent.handoffs import CritiqueReport
from agent.state import GigBidState

GENERIC_FLUFF = [
    "dear hiring manager", "dear sir", "dear madam", "to whom it may concern",
    "i am an expert", "i am confident i can do this"
]

def critic_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    if not draft:
        return {"critique": CritiqueReport(passed=False, score=0.0, feedback="No proposal draft found.", iteration_count=0)}

    letter = draft.cover_letter.lower()
    words = re.findall(r"\w+", letter)
    word_count = len(words)
    iteration = draft.iteration_count

    score = 1.0
    feedback_notes = []

    # 1. Check generic fluff
    has_fluff = any(f in letter for f in GENERIC_FLUFF)
    if has_fluff:
        score -= 0.40
        feedback_notes.append("Generic greeting or boilerplate detected; rewrite opening to be direct and technical.")

    # 2. Check evidence grounding citation
    if not draft.evidence_ids:
        score -= 0.30
        feedback_notes.append("No portfolio evidence cited; must ground claims in a verified project.")

    # 3. Check length
    if word_count < 60:
        score -= 0.30
        feedback_notes.append(f"Proposal too brief ({word_count} words); elaborate on architecture.")
    elif word_count > 400:
        score -= 0.20
        feedback_notes.append(f"Proposal overly verbose ({word_count} words); tighten paragraphs.")

    passed = (score >= 0.70) or (iteration >= 2) # Limit to at most 2 loops
    feedback = " ".join(feedback_notes) if feedback_notes else "Proposal satisfies grounding, length, and personalization standards."

    critique = CritiqueReport(
        passed=passed,
        score=max(0.0, min(1.0, round(score, 2))),
        feedback=feedback,
        iteration_count=iteration
    )
    return {"critique": critique}
