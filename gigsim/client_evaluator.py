import re
from typing import Dict, Any, List
from gigsim.models import Job, ProposalSubmission, ClientDecision

GENERIC_OPENING_PATTERNS = [
    r"dear hiring manager",
    r"dear sir/?madam",
    r"to whom it may concern",
    r"i am a (highly|very)? motivated",
    r"i have read your job (description|post) with (great)? interest",
    r"i am confident i can do this (job|project) perfectly",
    r"i am an expert with \d+ years of experience in programming"
]

class ClientEvaluator:
    @staticmethod
    def evaluate(job: Job, proposal: ProposalSubmission) -> ClientDecision:
        letter = proposal.cover_letter.lower()
        score = 0.5  # Base score

        # 1. Check for generic openings (Disliked by GigSim clients)
        has_generic = any(re.search(pat, letter) for pat in GENERIC_OPENING_PATTERNS)
        if has_generic:
            score -= 0.35
            generic_feedback = "Client was turned off by generic, canned proposal opening."
        else:
            score += 0.15
            generic_feedback = "Strong tailored opening addressing client's specific problem."

        # 2. Evidence citations grounding
        if proposal.evidence_ids and len(proposal.evidence_ids) > 0:
            score += 0.25
            evidence_feedback = f"Grounded with {len(proposal.evidence_ids)} verifiable portfolio items."
        else:
            score -= 0.15
            evidence_feedback = "Lacks verifiable portfolio evidence links."

        # 3. Required skills coverage
        matched_skills = [s for s in job.required_skills if s.lower() in letter]
        skill_ratio = len(matched_skills) / max(len(job.required_skills), 1)
        score += skill_ratio * 0.20

        # 4. Pricing / budget check
        b_max = job.budget.get("max", 5000)
        if proposal.bid_amount > b_max * 1.3:
            score -= 0.25
            budget_feedback = f"Bid ${proposal.bid_amount} significantly exceeded client budget ceiling (${b_max})."
        elif proposal.bid_amount < job.budget.get("min", 100) * 0.5:
            score -= 0.15
            budget_feedback = "Bid suspiciously low; raised quality concerns."
        else:
            score += 0.10
            budget_feedback = "Fair, competitive price quote."

        # 5. Screening questions answered
        if job.screening_questions:
            if proposal.screening_answers and len(proposal.screening_answers) >= len(job.screening_questions):
                score += 0.10
            else:
                score -= 0.15

        # Normalize score
        quality_score = max(0.0, min(1.0, round(score, 2)))

        # Probabilistic decision based on score
        replied = quality_score >= 0.60
        interview_offered = quality_score >= 0.75
        hired = quality_score >= 0.88

        feedback_parts = [generic_feedback, evidence_feedback, budget_feedback]
        if not replied:
            feedback_parts.append("Proposal ignored due to low relevance / weak differentiation.")
        elif interview_offered:
            feedback_parts.append("Client invited freelancer for an introductory call.")
        if hired:
            feedback_parts.append("Contract awarded to freelancer!")

        return ClientDecision(
            proposal_id=f"prop-eval-{job.job_id}",
            job_id=job.job_id,
            replied=replied,
            interview_offered=interview_offered,
            hired=hired,
            quality_score=quality_score,
            client_feedback=" ".join(feedback_parts)
        )
