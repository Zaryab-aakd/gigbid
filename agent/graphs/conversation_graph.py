from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from agent.state import ConversationState
from agent.nodes.client_liaison import client_liaison_node
from mcp_servers.marketplace.server import send_message_tool
from mcp_servers.workspace.server import create_interview_hold

def message_approval_node(state: ConversationState) -> Dict[str, Any]:
    # Interrupt for human review of drafted message
    user_decision = interrupt({
        "action": "client_message_approval_required",
        "client_id": state.get("client_id"),
        "job_id": state.get("job_id"),
        "intent": state.get("intent"),
        "draft_reply": state.get("draft_reply"),
        "proposed_slots": state.get("proposed_slots", [])
    })

    status = user_decision.get("status", "approved")
    edited_reply = user_decision.get("draft_reply")
    return {
        "approval_status": status,
        "draft_reply": edited_reply or state.get("draft_reply")
    }

def send_approved_message_node(state: ConversationState) -> Dict[str, Any]:
    if state.get("approval_status") == "approved":
        client_id = state.get("client_id", "")
        job_id = state.get("job_id", "")
        reply_text = state.get("draft_reply", "")
        
        # If interview request with slots, place tentative hold
        if state.get("intent") == "interview_request" and state.get("proposed_slots"):
            first_slot = state["proposed_slots"][0]
            create_interview_hold(
                title=f"Interview with {client_id}",
                start_time=first_slot["start"],
                duration_minutes=45
            )

        send_message_tool(client_id=client_id, job_id=job_id, text=reply_text, sender="freelancer")
        return {"approval_status": "sent"}
    return {"approval_status": "rejected"}

def route_conversation_approval(state: ConversationState) -> Literal["send_message", "end"]:
    if state.get("approval_status") == "approved":
        return "send_message"
    return "end"

def build_conversation_graph(checkpointer=None):
    workflow = StateGraph(ConversationState)

    workflow.add_node("client_liaison", client_liaison_node)
    workflow.add_node("message_approval", message_approval_node)
    workflow.add_node("send_message", send_approved_message_node)

    workflow.add_edge(START, "client_liaison")
    workflow.add_edge("client_liaison", "message_approval")
    workflow.add_conditional_edges(
        "message_approval",
        route_conversation_approval,
        {"send_message": "send_message", "end": END}
    )
    workflow.add_edge("send_message", END)

    cp = checkpointer or MemorySaver()
    return workflow.compile(checkpointer=cp)
