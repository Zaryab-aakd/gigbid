import re
from typing import Dict, Any, List
from agent.handoffs import ComplianceVerdict
from agent.state import GigBidState

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
TELEGRAM_REGEX = r"(t\.me/\w+|@\w+)"

def compliance_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    if not draft:
        return {"compliance_verdict": ComplianceVerdict(compliant=True, sanitized_letter="", actions_taken=[])}

    letter = draft.cover_letter
    actions = []
    violations = []

    # 1. Strip external contact info (POL-001)
    if re.search(EMAIL_REGEX, letter):
        violations.append("POL-001: Detected email address before contract")
        letter = re.sub(EMAIL_REGEX, "[CONTACT REMOVED PER PLATFORM POLICY]", letter)
        actions.append("Redacted pre-contract email address")

    if re.search(PHONE_REGEX, letter):
        violations.append("POL-001: Detected phone number before contract")
        letter = re.sub(PHONE_REGEX, "[PHONE NUMBER REDACTED]", letter)
        actions.append("Redacted phone number")

    # 2. Strip absolute false guarantees (POL-005)
    guarantee_patterns = [r"100%\s*(bug-free|guaranteed)", r"guarantee\s*zero\s*bugs"]
    for gp in guarantee_patterns:
        if re.search(gp, letter, re.IGNORECASE):
            violations.append("POL-005: Prohibited absolute guarantee clause")
            letter = re.sub(gp, "rigorous automated test coverage", letter, flags=re.IGNORECASE)
            actions.append("Rewrote absolute guarantee into defensible engineering projection")

    # Update draft with sanitized text
    draft.cover_letter = letter

    verdict = ComplianceVerdict(
        compliant=len(violations) == 0 or len(actions) > 0,
        violations=violations,
        sanitized_letter=letter,
        actions_taken=actions
    )
    return {
        "compliance_verdict": verdict,
        "proposal_draft": draft
    }
