import re
from typing import List, Dict, Any

def split_into_claims(draft: str) -> List[str]:
    """
    Split a cover letter or draft into individual atomic assertions / sentences.
    """
    # Clean and split on punctuation boundaries
    sentences = re.split(r"(?<=[.!?])\s+", draft.strip())
    claims = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) > 15 and not s_clean.lower().startswith(("hi ", "hello", "dear", "thanks", "best regards")):
            claims.append(s_clean)
    return claims

def check_claim_support(claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    claim_lower = claim.lower()
    claim_words = set(re.findall(r"\w+", claim_lower))
    
    # Check for hallucination red flags (unverified absolute claims)
    hallucination_phrases = [
        "100% guarantee", "guaranteed zero bugs", "guaranteed #1 ranking",
        "20 years experience with langgraph", "developed chatgpt", "invented python"
    ]
    for hp in hallucination_phrases:
        if hp in claim_lower:
            return {
                "claim": claim,
                "status": "unsupported",
                "evidence_id": None,
                "confidence": 0.05,
                "reason": f"Flagged policy violation: impossible or unverified claim ('{hp}')."
            }

    best_match_id = None
    best_overlap = 0.0

    for item in evidence:
        item_text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('text', '')} {' '.join(item.get('skills', []))}".lower()
        item_words = set(re.findall(r"\w+", item_text))
        
        # Calculate Jaccard / token overlap
        overlap = len(claim_words.intersection(item_words)) / max(len(claim_words), 1)
        
        # Check skill overlap
        skills = [s.lower() for s in item.get("skills", [])]
        skill_hit = any(s in claim_lower for s in skills)
        if skill_hit:
            overlap += 0.35

        if overlap > best_overlap:
            best_overlap = overlap
            best_match_id = item.get("evidence_id") or item.get("chunk_id")

    if best_overlap >= 0.50:
        status = "supported"
        reason = f"Grounded in verified portfolio item {best_match_id}."
    elif best_overlap >= 0.30:
        status = "partly_supported"
        reason = f"Partially matches concepts in portfolio item {best_match_id}."
    else:
        status = "unsupported"
        reason = "No supporting evidence found in verified portfolio."

    return {
        "claim": claim,
        "status": status,
        "evidence_id": best_match_id if status != "unsupported" else None,
        "confidence": round(min(1.0, best_overlap), 2),
        "reason": reason
    }

def verify_claims(draft: str, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Split the draft into atomic claims and label each:
    supported, partly_supported, or unsupported.
    """
    claims = split_into_claims(draft)
    results = [check_claim_support(c, evidence) for c in claims]
    return results

def sanitize_draft(draft: str, verification_results: List[Dict[str, Any]]) -> str:
    """
    Remove or rewrite unsupported claims before the Critic or Marketplace sees the draft.
    """
    cleaned = draft
    for res in verification_results:
        if res["status"] == "unsupported":
            # Strip the unsupported claim from the text
            claim_text = res["claim"]
            cleaned = cleaned.replace(claim_text, "").strip()
    
    # Clean up double whitespace
    cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
    return cleaned
