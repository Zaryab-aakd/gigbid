import re
from typing import Dict, Any, List
from agent.handoffs import RiskReport
from agent.state import GigBidState

SCAM_PATTERNS = [
    (r"telegram\s*(@\w+|:\s*\w+)", "off_platform_telegram"),
    (r"whatsapp\s*(\+?\d+|:\s*\d+)", "off_platform_whatsapp"),
    (r"(pay|contact)\s*outside\s*(upwork|platform)", "off_platform_contact"),
    (r"free\s*(trial|test|sample)\s*(for\s*free|before\s*hire)", "unpaid_trial_work"),
    (r"crypto\s*(gas\s*fee|deposit|usdt)", "crypto_fee_scam"),
    (r"\.(exe|scr|bat|vbs)\b", "malicious_file_attachment")
]

PROMPT_INJECTION_PATTERNS = [
    r"system\s*override",
    r"ignore\s*(all\s*)?previous\s*instructions",
    r"disregard\s*(all\s*)?prior\s*commands",
    r"new\s*instructions?:",
    r"admin\s*command:",
    r"prompt\s*leak"
]

def risk_assessor_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    desc = job.get("description", "")
    flags: List[str] = []
    
    # Check client profile risk
    client = job.get("client", {})
    if client:
        hire_rate = client.get("hire_rate", 1.0)
        hires = client.get("hires", 1)
        rating = client.get("rating", 5.0)
        if hire_rate < 0.15 and hires > 5:
            flags.append("low_client_hire_rate")
        if rating < 3.5 and hires > 2:
            flags.append("poor_client_rating")

    # Check scam patterns
    is_scam = False
    for pat, tag in SCAM_PATTERNS:
        if re.search(pat, desc, re.IGNORECASE):
            flags.append(tag)
            is_scam = True

    # Check prompt injection patterns
    has_injection = False
    sanitized_desc = desc
    for pat in PROMPT_INJECTION_PATTERNS:
        match = re.search(pat, desc, re.IGNORECASE)
        if match:
            flags.append("prompt_injection_attempt")
            has_injection = True
            # Strip injection text
            sanitized_desc = re.sub(pat + r"[^\n]*", "[REDACTED UNTRUSTED INJECTION]", sanitized_desc, flags=re.IGNORECASE)

    score = 0.05
    if is_scam:
        score += 0.80
    if has_injection:
        score += 0.25
    if len(flags) > 2:
        score += 0.20
    
    risk_score = min(1.0, round(score, 2))
    explanation = f"Detected {len(flags)} safety flags: {', '.join(flags)}." if flags else "No risk signals identified; client profile verified."

    report = RiskReport(
        score=risk_score,
        is_scam=is_scam,
        prompt_injection_detected=has_injection,
        flags=flags,
        sanitized_description=sanitized_desc,
        explanation=explanation
    )
    return {"risk_report": report}
