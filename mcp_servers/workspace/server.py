import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WorkspaceServer", dependencies=["pydantic"])

# Local mock persistence for calendar holds and email drafts
CALENDAR_HOLDS: List[Dict[str, Any]] = []
EMAIL_DRAFTS: List[Dict[str, Any]] = []

@mcp.tool(
    name="get_calendar_availability",
    description="Check free interview slots over the coming days."
)
def get_calendar_availability(days_ahead: int = 5) -> List[Dict[str, str]]:
    """Return available 45-minute interview windows."""
    slots = []
    base_time = datetime.now(timezone.utc) + timedelta(days=1)
    for i in range(days_ahead):
        day = base_time + timedelta(days=i)
        if day.weekday() < 5:  # Monday to Friday
            slots.append({
                "slot_id": f"slot-{day.strftime('%Y%m%d')}-10am",
                "start": day.replace(hour=10, minute=0, second=0).isoformat(),
                "end": day.replace(hour=10, minute=45, second=0).isoformat(),
                "timezone": "UTC"
            })
            slots.append({
                "slot_id": f"slot-{day.strftime('%Y%m%d')}-2pm",
                "start": day.replace(hour=14, minute=0, second=0).isoformat(),
                "end": day.replace(hour=14, minute=45, second=0).isoformat(),
                "timezone": "UTC"
            })
    return slots

@mcp.tool(
    name="create_interview_hold",
    description="Place a tentative interview hold on the calendar for a client meeting."
)
def create_interview_hold(
    title: str,
    start_time: str,
    duration_minutes: int = 45,
    client_email: Optional[str] = None
) -> Dict[str, Any]:
    """Create a tentative calendar hold."""
    hold_id = f"hold-{uuid.uuid4().hex[:8]}"
    hold = {
        "hold_id": hold_id,
        "title": title,
        "start_time": start_time,
        "duration_minutes": duration_minutes,
        "client_email": client_email or "client@example.com",
        "status": "tentative_hold",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    CALENDAR_HOLDS.append(hold)
    return hold

@mcp.tool(
    name="create_email_draft",
    description="Create an email draft in the mailbox (requires human review before sending)."
)
def create_email_draft(
    to_email: str,
    subject: str,
    body: str
) -> Dict[str, Any]:
    """Create an unsent email draft."""
    draft_id = f"draft-{uuid.uuid4().hex[:8]}"
    draft = {
        "draft_id": draft_id,
        "to_email": to_email,
        "subject": subject,
        "body": body,
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    EMAIL_DRAFTS.append(draft)
    return draft

@mcp.tool(
    name="list_workspace_activity",
    description="List created calendar holds and email drafts."
)
def list_workspace_activity() -> Dict[str, Any]:
    return {
        "calendar_holds": CALENDAR_HOLDS,
        "email_drafts": EMAIL_DRAFTS
    }

if __name__ == "__main__":
    mcp.run()
