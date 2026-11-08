import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from agent.memory.promotion_rules import PromotionRules

class MemoryStore:
    def __init__(self):
        self.style_memory: List[Dict[str, Any]] = [
            {
                "memory_id": "mem-style-001",
                "type": "style",
                "rule": "RULE_DELETE_GENERIC_OPENINGS",
                "preference": "Always open with the technical problem statement rather than 'Dear Hiring Manager'.",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        self.outcome_memory: List[Dict[str, Any]] = [
            {
                "memory_id": "mem-out-001",
                "type": "outcome",
                "evidence_id": "case-ai-001",
                "outcome": "won",
                "win_count": 8,
                "notes": "Consistently wins enterprise AI/ML contracts.",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

    def record_user_edit(self, original_text: str, edited_text: str) -> Optional[Dict[str, Any]]:
        promoted = PromotionRules.should_promote_style_edit(original_text, edited_text)
        if promoted:
            entry = {
                "memory_id": f"mem-style-{uuid.uuid4().hex[:6]}",
                "type": "style",
                "rule": promoted["rule"],
                "preference": promoted["preference"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.style_memory.append(entry)
            return entry
        return None

    def record_outcome(self, proposal_data: Dict[str, Any], client_outcome: str) -> Optional[Dict[str, Any]]:
        promoted = PromotionRules.should_promote_outcome(proposal_data, client_outcome)
        if promoted:
            entry = {
                "memory_id": f"mem-out-{uuid.uuid4().hex[:6]}",
                "type": "outcome",
                "evidence_ids": promoted["evidence_ids"],
                "outcome": promoted["outcome"],
                "weight_delta": promoted["weight_delta"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.outcome_memory.append(entry)
            return entry
        return None

    def list_all_memories(self) -> List[Dict[str, Any]]:
        return self.style_memory + self.outcome_memory

    def delete_memory(self, memory_id: str) -> bool:
        init_len = len(self.style_memory) + len(self.outcome_memory)
        self.style_memory = [m for m in self.style_memory if m["memory_id"] != memory_id]
        self.outcome_memory = [m for m in self.outcome_memory if m["memory_id"] != memory_id]
        return (len(self.style_memory) + len(self.outcome_memory)) < init_len

memory_store = MemoryStore()
