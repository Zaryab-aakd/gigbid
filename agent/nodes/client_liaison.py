import re
from typing import Dict, Any
from agent.state import ConversationState
from mcp_servers.workspace.server import get_calendar_availability, create_interview_hold

def client_liaison_node(state: ConversationState) -> Dict[str, Any]:
    msg = state.get("incoming_message", "").lower()
    client_id = state.get("client_id", "client-unknown")

    # Intent Classification
    if any(kw in msg for kw in ["call", "meet", "interview", "zoom", "chat", "discuss", "time", "slot", "availability"]):
        intent = "interview_request"
        slots = get_calendar_availability(days_ahead=3)
        proposed_slots = slots[:3]
        slot_texts = [f"- {s['start']} UTC" for s in proposed_slots]
        draft = (
            f"Hi! Thank you for getting back to me. I'd be happy to hop on a call to discuss the project details. "
            f"Here are a few slots that work well for me:\n" + "\n".join(slot_texts) + "\n\nDoes one of these suit your schedule?"
        )
    elif any(kw in msg for kw in ["rate", "discount", "price", "budget", "cheaper", "expensive"]):
        intent = "negotiation"
        proposed_slots = []
        draft = (
            "Hi! Thanks for bringing this up. My proposed rate reflects the end-to-end architecture, strict test coverage, "
            "and production guarantees I deliver. However, if needed, we can phase the project scope so the initial MVP fits comfortably within your immediate budget."
        )
    elif any(kw in msg for kw in ["telegram", "whatsapp", "crypto", "outside", "wire"]):
        intent = "spam"
        proposed_slots = []
        draft = "Notice: All communication and payments must remain securely within the platform per terms of service."
    else:
        intent = "question"
        proposed_slots = []
        draft = (
            "Hi! Thanks for the question. Yes, I have handled similar requirements in production. "
            "I'd be glad to share an architecture outline or jump on a quick call to address any specifics."
        )

    return {
        "intent": intent,
        "proposed_slots": proposed_slots,
        "draft_reply": draft,
        "approval_status": "pending_approval"
    }
