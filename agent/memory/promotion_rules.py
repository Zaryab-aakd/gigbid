from typing import Dict, Any, Optional

class PromotionRules:
    @staticmethod
    def should_promote_style_edit(original_text: str, edited_text: str) -> Optional[Dict[str, Any]]:
        """
        Rule: An edit is promoted to style memory ONLY if:
        1. Length delta is significant (> 15% change in length or distinct phrasing)
        2. Consistent structural change (e.g., deleted generic opening or replaced greeting)
        """
        if not original_text or not edited_text:
            return None
        
        orig_words = original_text.strip().split()
        edit_words = edited_text.strip().split()

        if len(orig_words) == 0:
            return None

        ratio = abs(len(edit_words) - len(orig_words)) / len(orig_words)
        
        # Check if user deleted common generic phrases
        deleted_phrases = []
        for phrase in ["dear hiring manager", "i am an expert", "i have read your job description"]:
            if phrase in original_text.lower() and phrase not in edited_text.lower():
                deleted_phrases.append(phrase)

        if deleted_phrases:
            return {
                "rule": "RULE_DELETE_GENERIC_OPENINGS",
                "pattern": deleted_phrases,
                "preference": "Always use concise, direct technical openings without canned greetings.",
                "confidence": 0.95
            }

        if ratio > 0.20:
            return {
                "rule": "RULE_CONCISE_PROPOSAL_LENGTH",
                "preference": f"User prefers {'shorter' if len(edit_words) < len(orig_words) else 'longer'} proposal format.",
                "confidence": 0.85
            }

        return None

    @staticmethod
    def should_promote_outcome(proposal_data: Dict[str, Any], client_outcome: str) -> Optional[Dict[str, Any]]:
        """
        Rule: An outcome is promoted to long-term memory ONLY if:
        1. Explicit platform outcome verified: 'won' or 'replied' (positive) or 'ignored' (negative)
        2. Associated evidence ID is recorded
        """
        if client_outcome not in ["won", "replied", "ignored"]:
            return None

        evidence_ids = proposal_data.get("evidence_ids", [])
        return {
            "rule": "RULE_OUTCOME_GROUNDING_REINFORCEMENT",
            "outcome": client_outcome,
            "evidence_ids": evidence_ids,
            "weight_delta": +0.25 if client_outcome == "won" else (+0.10 if client_outcome == "replied" else -0.15)
        }
