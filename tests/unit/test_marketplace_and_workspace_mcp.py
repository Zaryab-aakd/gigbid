from mcp_servers.marketplace.server import (
    search_jobs_tool,
    get_job_tool,
    get_client_history_tool,
    get_connects_balance_tool,
    submit_proposal_tool,
    send_message_tool,
    list_messages_tool
)
from mcp_servers.workspace.server import (
    get_calendar_availability,
    create_interview_hold,
    create_email_draft,
    list_workspace_activity
)

def test_marketplace_mcp_read_tools():
    jobs = search_jobs_tool(limit=3)
    assert len(jobs) == 3
    job_id = jobs[0]["job_id"]

    job = get_job_tool(job_id)
    assert "job_id" in job
    assert job["job_id"] == job_id

    balance = get_connects_balance_tool()
    assert "current_balance" in balance

def test_marketplace_mcp_proposal_and_idempotency():
    jobs = search_jobs_tool(limit=1)
    job_id = jobs[0]["job_id"]

    # 1. Dry run
    res_dry = submit_proposal_tool(
        job_id=job_id,
        freelancer_id="ai_ml_engineer",
        cover_letter="I have built multi-agent RAG pipelines in LangGraph with 98% citation accuracy.",
        bid_amount=1500.0,
        idempotency_key="mcp-test-key-1",
        evidence_ids=["case-ai-001"],
        dry_run=True
    )
    assert res_dry["dry_run"] is True
    assert res_dry["status"] == "preview"

    # 2. Real submission
    res_real = submit_proposal_tool(
        job_id=job_id,
        freelancer_id="ai_ml_engineer",
        cover_letter="I have built multi-agent RAG pipelines in LangGraph with 98% citation accuracy.",
        bid_amount=1500.0,
        idempotency_key="mcp-test-key-2",
        evidence_ids=["case-ai-001"],
        dry_run=False
    )
    assert res_real["status"] == "submitted"

    # 3. Repeat call with SAME key -> Idempotent
    res_dup = submit_proposal_tool(
        job_id=job_id,
        freelancer_id="ai_ml_engineer",
        cover_letter="I have built multi-agent RAG pipelines in LangGraph with 98% citation accuracy.",
        bid_amount=1500.0,
        idempotency_key="mcp-test-key-2",
        evidence_ids=["case-ai-001"],
        dry_run=False
    )
    assert res_dup["proposal_id"] == res_real["proposal_id"]

def test_workspace_mcp():
    slots = get_calendar_availability(days_ahead=3)
    assert len(slots) > 0
    first_slot = slots[0]
    assert "start" in first_slot

    hold = create_interview_hold(
        title="Intro call with Client",
        start_time=first_slot["start"],
        duration_minutes=45,
        client_email="client@acme.corp"
    )
    assert hold["status"] == "tentative_hold"
    assert hold["client_email"] == "client@acme.corp"

    draft = create_email_draft(
        to_email="client@acme.corp",
        subject="Follow-up on Architecture Discussion",
        body="Thank you for the time today. Attached is our proposed milestone schedule."
    )
    assert draft["status"] == "draft"

    activity = list_workspace_activity()
    assert len(activity["calendar_holds"]) >= 1
    assert len(activity["email_drafts"]) >= 1
